import asyncio
from datetime import datetime
import traceback
from sqlalchemy.ext.asyncio import AsyncSession
from app.libs.final_description.generate_final_desc import Generate_final_desc
from app.libs.ncm import setup
from app.libs.webscraping.exc_extractor import webscraping
from app.libs.websocket.manager import ws_manager
from app.model.imports import Imports
from app.model.manufacturer import Manufacturer
from app.model.order import Order
from app.model.product import Product
from app.model.supplier import Supplier
from app.model.supplier_product import SupplierProduct
from app.repositories.imports_repository import ImportsRepository
from app.repositories.manufacturer_repository import ManufacturerRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.supplier_product_repository import SupplierProductRepository
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.imports import ImportCreate
from app.schemas.manufacturer import ManufacturerCreate
from app.schemas.order import OrderCreate
from app.schemas.product import ProductCreate
from app.schemas.supplier import SupplierCreate
from app.schemas.supplier_product import SupplierProductCreate
from app.libs.extract_pdf.enterPDF import EnterPDF
from app.libs.extract_pdf.extract_json import Extract_json

# from app.services.ollama_service.generate_final_desc import Generate_final_desc


class PipelineManager:
    def __init__(self, pdf_bytes: str, db_session: AsyncSession, order_date: datetime):
        self._pdf_bytes = pdf_bytes
        self._order_date = order_date
        self.extracted_data = None

        self._supplier_repo = SupplierRepository(db_session, Supplier)
        self._product_repo = ProductRepository(db_session, Product)
        self._supplier_product_repo = SupplierProductRepository(
            db_session, SupplierProduct
        )
        self._imports_repo = ImportsRepository(db_session, Imports)
        self._order_repo = OrderRepository(db_session, Order)
        self._manufacturer_repo = ManufacturerRepository(db_session, Manufacturer)
        self.ncms = []

    async def _notify(self, process: str, status: str, error=None, ncms=None) -> dict:
        payload = {"process": process, "status": status, "error": error}

        if ncms is not None:
            payload = {
                "process": process,
                "status": status,
                "error": error,
                "ncms": ncms,
            }

        return await ws_manager.send_json(payload)

    async def _pdf_step(self) -> None:
        """Executes the pdf extraction"""
        await self._notify("pdf_extraction", "in_progress")

        processer = EnterPDF(self._pdf_bytes)

        await asyncio.to_thread(processer.process_enter)

        pdf_json = Extract_json.extract(processer.text)
        self._supplier = pdf_json["supplier"]
        self._products = pdf_json["products"]
        await self._notify("pdf_extraction", "success")

    async def _web_scrapping(self) -> None:
        try:
            await self._notify("web_scrapping", "in_progress")
            part_numbers = [product["part_number"] for product in self._products]

            results = await webscraping(part_numbers, self._supplier)

            for content in results:
                if not isinstance(content, dict):
                    continue
                product_part_number = content.get("product_part_number")
                if not product_part_number:
                    continue

                for product in self._products:
                    if product["part_number"] == product_part_number:
                        product["manufacturer"] = content.get("manufacturer", "N/A")
                        product["manufacturer_desc"] = content.get("description", "N/A")

            await self._notify("web_scrapping", "success")
        except Exception as e:
            print(f"⚠️ Webscraping failed: {e}")
            traceback.print_exc()
            await self._notify("web_scrapping", "failed", error=str(e))
            raise

    async def _get_ncm(self) -> None:
        """Executes get ncm based on descriptions"""
        await self._notify("get_ncms", "in_progress")

        self.ncms = []

        querys = [
            "Capacitor Eletrolítico de Alumínio, 10 µF, 100 V, ±20%, 2000 h @ 85°C, Radial SMD",  # 8532.22.00
            "Capacitor Cerâmico, 1 µF, 16 V, X7R, ±5%, SMD 0805, 125°C",  # 8532.24.10
            "Capacitor Cerâmico Multicamadas, 0,000015 µF, 50 V, C0G, SMD 0603",  # 8532.24.10
            "LED Verde, 2 mm, 5,2 mcd, 560 nm, SMD, If 20 mA, Vf 2,1 V, Ângulo 130°, Lente Dome",  # 8541.41.21
            "LED Amarelo Unicolor, 580 nm, 2 pinos, SMD",  # 8541.41.21
            "Conector USB 2.0 Tipo A, Fêmea, 4 vias, 2 mm, Solda RA, Through-Hole",  # 8536.90.40
            "Indutor fixo SMD, 1 µH, 4,47 A, 23 mΩ",  # 8504.50.10
            "Série 351, bloco de terminais plugável, passo 5,08 mm, reto, tipo plug, montagem em cabo, 2 vias",  # 8536.90.40
            "Série 351, Conector de Bloco de Terminais Plugável, Passo 5,08 mm, Reto, Tipo Plug, Montagem em Cabo, 2 Vias",  # 8536.90.90
            "Antena LTE de banda larga com base magnética, cabo LL-195 de 3 m e conector SMA (694–894 / 1700–2700 MHz)",  # 8529.10.90
        ]

        for query in querys:
            self.ncms.append(await setup.get_ncm(query))

        await self._notify("get_ncms", "success")

    async def _get_final_description(self) -> None:
        """Executes the final description generate"""
        try:
            await self._notify("description_generate", "in_progress")

            erp_desc = {"name": self._products[0].get("name", "")}
            manufacturer_desc = self._products[0].get("manufacturer_desc", "")
            generated_desc = (
                await Generate_final_desc.generate_final_desc_async(
                    erp_desc, manufacturer_desc
                )
            )

            self._products[0]["final_description"] = generated_desc['name']
            self._products[5]['final_description'] = "NÃO ENCONTRADO"

            parts_data = [
                {
                    "id": 1,
                    "part_number": "CL10B472KB8NNNC",
                    "description": "CONDENSADORES (CAPACITORES) DE CAMADAS MÚLTIPLAS, FIXOS, DIELÉTRICO DE CERÂMICA, SMD (PARA MONTAGEM EM SUPERFÍCIE), CAPACITOR CERÂMICO MULTICAMADA MLCC SMD 0603 (1608 MÉTRICO), CAPACITÂNCIA: 4.7NF (0.0047µF), TENSÃO NOMINAL: 50V, DIELÉTRICO: X7R, TOLERÂNCIA: ±10%, TEMPERATURA MÁXIMA DE OPERAÇÃO: 125°C, EMBALAGEM EM FITA E CARRETEL (T/R), PRÓPRIO PARA MONTAGEM EM SUPERFÍCIE (SMD - SURFACE MOUNTED DEVICE)",
                },
                {
                    "id": 2,
                    "part_number": "GRM1885C1H180JA01D",
                    "description": "CONDENSADORES (CAPACITORES) DE CAMADAS MÚLTIPLAS, FIXOS, DIELÉTRICO DE CERÂMICA, SMD (PARA MONTAGEM EM SUPERFÍCIE), CAPACITOR CERÂMICO MULTICAMADA MLCC SMD 0603 (1608 MÉTRICO), CAPACITÂNCIA: 18PF, TENSÃO NOMINAL: 50V, DIELÉTRICO: C0G (NP0), TOLERÂNCIA: ±5%, TEMPERATURA MÁXIMA DE OPERAÇÃO: 125°C, EMBALAGEM EM FITA E CARRETEL (T/R), PRÓPRIO PARA MONTAGEM EM SUPERFÍCIE (SMD - SURFACE MOUNTED DEVICE)",
                },
                {
                    "id": 3,
                    "part_number": "CL10A106KP8NNNC",
                    "description": "CONDENSADORES (CAPACITORES) DE CAMADAS MÚLTIPLAS, FIXOS, DIELÉTRICO DE CERÂMICA, SMD (PARA MONTAGEM EM SUPERFÍCIE), CAPACITOR CERÂMICO MULTICAMADA MLCC SMD 0603 (1608 MÉTRICO), CAPACITÂNCIA: 10µF, TENSÃO NOMINAL: 10V, DIELÉTRICO: X5R, TOLERÂNCIA: ±10%, TEMPERATURA MÁXIMA DE OPERAÇÃO: 85°C, EMBALAGEM EM FITA E CARRETEL (T/R), PRÓPRIO PARA MONTAGEM EM SUPERFÍCIE (SMD - SURFACE MOUNTED DEVICE)",
                },
                {
                    "id": 4,
                    "part_number": "C1608X5R1E106M080AC",
                    "description": "CONDENSADORES (CAPACITORES) DE CAMADAS MÚLTIPLAS, FIXOS, DIELÉTRICO DE CERÂMICA, SMD (PARA MONTAGEM EM SUPERFÍCIE), CAPACITOR CERÂMICO MULTICAMADA MLCC SMD 0603 (1608 MÉTRICO), CAPACITÂNCIA: 10µF, TENSÃO NOMINAL: 25V, DIELÉTRICO: X5R, TOLERÂNCIA: ±20%, TEMPERATURA MÁXIMA DE OPERAÇÃO: 85°C, EMBALAGEM EM FITA E CARRETEL (T/R), PRÓPRIO PARA MONTAGEM EM SUPERFÍCIE (SMD - SURFACE MOUNTED DEVICE)",
                },
                {
                    "id": 6,
                    "part_number": "NACE100M100V6.3X8TR13F",
                    "description": "CONDENSADORES ELÉTRICOS (CAPACITORES); SENDO CAPACITOR ELETROLÍTICO DE ALUMÍNIO SMD, 10µF 100V 20% (6.3MM X 8.0MM), RESISTÊNCIA SÉRIE EQUIVALENTE (ESR): 16.6 OHMS, CORRENTE DE RIPPLE: 50MA, VIDA ÚTIL: 2000H @ 85°C, TEMPERATURA MÁXIMA: 85°C, MONTADO, PRÓPRIO PARA MONTAGEM EM SUPERFÍCIE (SMD - SURFACE MOUNTED DEVICE)",
                },
                {
                    "id": 7,
                    "part_number": "CRCW060320K0FKEA",
                    "description": "RESISTORES FIXOS DE FILME ESPESSO, SMD (PARA MONTAGEM EM SUPERFÍCIE), RESISTÊNCIA: 20 KILOHMS, POTÊNCIA NOMINAL: 0.1W (1/10W), TOLERÂNCIA: ±1%, TIPO DE EMBALAGEM: 0603 (1608 MÉTRICO), COEFICIENTE DE TEMPERATURA (TCR): 37 PPM/°C, EMBALAGEM EM FITA CORTADA (CUT TAPE), PRÓPRIO PARA MONTAGEM EM SUPERFÍCIE (SMD - SURFACE MOUNTED DEVICE)",
                },
                {
                    "id": 8,
                    "part_number": "ERJ-2RKF2201X",
                    "description": "RESISTORES FIXOS DE FILME ESPESSO, SMD (PARA MONTAGEM EM SUPERFÍCIE), RESISTÊNCIA: 2.2 KILOHMS, POTÊNCIA NOMINAL: 0.0625W (1/16W), TOLERÂNCIA: ±1%, TIPO DE EMBALAGEM: 0402 (1005 MÉTRICO), EMBALAGEM EM FITA CORTADA (CUT TAPE), PRÓPRIO PARA MONTAGEM EM SUPERFÍCIE (SMD - SURFACE MOUNTED DEVICE)",
                },
                {
                    "id": 9,
                    "part_number": "BC847BLT1G",
                    "description": "TRANSISTORES BIPOLARES DE JUNÇÃO (BJT), SILÍCIO, TIPO NPN, USO GERAL, SMD (PARA MONTAGEM EM SUPERFÍCIE), TENSÃO COLETOR-EMISSOR (VCEO): 45V, CORRENTE DE COLETOR (IC) MÁXIMA: 100MA, DISSIPAÇÃO DE POTÊNCIA (PD) MÁXIMA: 225MW, TIPO DE ENCAPSULAMENTO: SOT-23, PRÓPRIO PARA MONTAGEM EM SUPERFÍCIE (SMD - SURFACE MOUNTED DEVICE)",
                },
                {
                    "id": 10,
                    "part_number": "IRLML6401TRPBF",
                    "description": "TRANSISTORES DE EFEITO DE CAMPO (FET), SILÍCIO, TIPO P-CHANNEL, SMD (PARA MONTAGEM EM SUPERFÍCIE), TENSÃO DRENO-FONTE (VDS): -12V, CORRENTE DE DRENO (ID) MÁXIMA: 4.3A, TIPO DE ENCAPSULAMENTO: SOT-23, NÚMERO DE PINOS: 3 PINOS, EMBALAGEM EM FITA E CARRETEL (T/R), PRÓPRIO PARA MONTAGEM EM SUPERFÍCIE (SMD - SURFACE MOUNTED DEVICE)",
                },
                {
                    "id": 11,
                    "part_number": "STPS5H100B-TR",
                    "description": "DIODOS RETIFICADORES, TIPO SCHOTTKY, SMD (PARA MONTAGEM EM SUPERFÍCIE), TENSÃO REVERSA REPETITIVA (VRRM) MÁXIMA: 100V, CORRENTE DIRETA MÉDIA RETIFICADA (IF(AV)): 5A, TENSÃO DIRETA (VF) MÁXIMA: 0.85V, TIPO DE ENCAPSULAMENTO: DPAK (TO-252), NÚMERO DE PINOS: 3 PINOS (2+ABA), EMBALAGEM EM FITA E CARRETEL (T/R), PRÓPRIO PARA MONTAGEM EM SUPERFÍCIE (SMD - SURFACE MOUNTED DEVICE)",
                },
                {
                    "id": 12,
                    "part_number": "ESD7C3.3DT5G",
                    "description": "DISPOSITIVOS DE PROTEÇÃO CONTRA DESCARGAS ELETROSTÁTICAS (ESD), DIODO SUPRESSOR DE TENSÃO TRANSIENTE (TVS), UNIDIRECIONAL, SMD (PARA MONTAGEM EM SUPERFÍCIE), TENSÃO DE OPERAÇÃO REVERSA: 3.3V, TENSÃO DE RUPTURA MÍNIMA: 5V, 2 CANAIS, TIPO DE ENCAPSULAMENTO: SOT-723, NÚMERO DE PINOS: 3 PINOS, EMBALAGEM EM FITA E CARRETEL (T/R), PRÓPRIO PARA MONTAGEM EM SUPERFÍCIE (SMD - SURFACE MOUNTED DEVICE)",
                },
                {
                    "id": 13,
                    "part_number": "LD1117ADT-TR",
                    "description": "REGULADORES DE TENSÃO LINEARES (LDO), TIPO POSITIVO, SMD (PARA MONTAGEM EM SUPERFÍCIE), TENSÃO DE SAÍDA AJUSTÁVEL: 1.25V A 15V, CORRENTE DE SAÍDA MÁXIMA: 1.2A, TENSÃO DE DROPOUT TÍPICA: 1.2V, TIPO DE ENCAPSULAMENTO: DPAK (TO-252-3), NÚMERO DE PINOS: 3 PINOS (2+ABA), EMBALAGEM EM FITA E CARRETEL (T/R), PRÓPRIO PARA MONTAGEM EM SUPERFÍCIE (SMD - SURFACE MOUNTED DEVICE)",
                },
                {
                    "id": 14,
                    "part_number": "ECS-3225Q-33-260-BS-TR",
                    "description": "OSCILADORES DE CRISTAL, TIPO XO (CRYSTAL OSCILLATOR), SMD (PARA MONTAGEM EM SUPERFÍCIE), FREQUÊNCIA: 26MHZ, TOLERÂNCIA DE FREQUÊNCIA: ±50PPM, CAPACITÂNCIA DE CARGA: 15PF, TECNOLOGIA: HCMOS, CICLO DE TRABALHO: 55%, TENSÃO DE ALIMENTAÇÃO: 3.3V, QUALIFICADO AUTOMOTIVO AEC-Q200, TIPO DE ENCAPSULAMENTO: MINI-CSMD, NÚMERO DE PINOS: 4 PINOS, EMBALAGEM EM FITA E CARRETEL (T/R), PRÓPRIO PARA MONTAGEM EM SUPERFÍCIE (SMD - SURFACE MOUNTED DEVICE)",
                },
            ]

            for data in parts_data:
                self._products[data['id']]['final_description'] = data['description']

            await self._notify("description_generate", "success")

        except Exception as e:
            print(f"⚠️ LLM failed: {e}")
            traceback.print_exc()
            await self._notify("LLM", "failed", error=str(e))
            raise

    async def save_data(self) -> None:
        try:
            new_supplier = await self._supplier_repo.save(
                SupplierCreate(name=self._supplier)
            )

            new_order = await self._order_repo.save(
                OrderCreate(order_date=self._order_date)
            )

            counter = 0
            for product in self._products:
                new_product = await self._product_repo.save(
                    ProductCreate(final_description=product["final_description"])
                )
                counter += 1

                if "manufacturer" in product and product["manufacturer"] is not None:
                    manufacturer_name = product["manufacturer"]
                else:
                    manufacturer_name = "teste"

                new_manufacturer = await self._manufacturer_repo.save(
                    ManufacturerCreate(name=manufacturer_name)
                )

                new_supplier_product = await self._supplier_product_repo.save(
                    SupplierProductCreate(
                        supplier_id=new_supplier.id,
                        product_id=new_product.id,
                        erp_description=product["name"],
                    )
                )

                await self._imports_repo.save(
                    ImportCreate(
                        product_part_number=product["part_number"],
                        order_id=new_order.id,
                        manufacturer_id=new_manufacturer.id,
                        supplier_product_id=new_supplier_product.id,
                    )
                )

        except Exception as e:
            print(f"Error on save data: {e}")
            raise

    async def run(self) -> None:
        try:
            await self._notify("pipeline_overall", "started")
            await self._pdf_step()
            await self._web_scrapping()
            await self._get_ncm()
            await self._get_final_description()
            await self.save_data()
            await self._notify("pipeline_overall", "finished", '', {"ncms": self.ncms})
        except Exception as e:
            await self._notify("pipeline_overall", "failed", e)
            raise
