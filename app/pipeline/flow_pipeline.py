from ast import Dict
import asyncio
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.log.logger import logger

from app.libs.ncm import setup
from app.libs.websocket.manager import ws_manager
from app.libs.extract_pdf.enter_pdf import EnterPDF
from app.libs.extract_pdf.extract_json import Extract_json
from app.libs.webscraping.exc_extractor import webscraping
from app.libs.final_description.generate_final_desc import Generate_final_desc

from app.schemas import (
    ImportCreate,
    ManufacturerCreate,
    OrderCreate,
    ProductCreate,
    SupplierCreate,
    SupplierProductCreate,
)

from app.model import (
    Imports,
    Manufacturer,
    Order,
    Product,
    Supplier,
    SupplierProduct,
)

from app.repositories import (
    ImportsRepository,
    ManufacturerRepository,
    OrderRepository,
    ProductRepository,
    SupplierRepository,
    SupplierProductRepository,
)


class PipelineManager:
    def __init__(self, pdf_bytes: str, db_session: AsyncSession, order_date: datetime):
        self._pdf_bytes = pdf_bytes
        self._order_date = order_date

        self._supplier_repo = SupplierRepository(db_session, Supplier)
        self._product_repo = ProductRepository(db_session, Product)

        self._supplier_product_repo = SupplierProductRepository(
            db_session, SupplierProduct
        )
        self._imports_repo = ImportsRepository(db_session, Imports)
        self._order_repo = OrderRepository(db_session, Order)
        self._manufacturer_repo = ManufacturerRepository(db_session, Manufacturer)

    async def _notify(
        self, process: str, status: str, error: str = None, data: dict = None
    ) -> dict | None:
        """Notify a process status and other additional infos"""
        try:
            payload = {"process": process, "status": status}

            if error:
                payload["error"] = error
            elif data:
                payload["data"] = data

            return await ws_manager.send_json(payload)
        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {e}")
            raise

    async def _pdf_step(self) -> None:
        """Executes the pdf extraction process"""
        try:
            await self._notify("pdf_extraction", "in_progress")

            pdf_processer = EnterPDF(self._pdf_bytes)

            await asyncio.to_thread(pdf_processer.process_enter)

            pdf_json = Extract_json.extract(pdf_processer.text)

            self._supplier = pdf_json["supplier"]
            self._products = pdf_json["products"]
            await self._notify("pdf_extraction", "success")
        except Exception as e:
            logger.error(f"Error to processing pdf: {e}")
            await self._notify("pdf_extraction", "error", error=str(e))
            raise

    async def _web_scrapping(self) -> None:
        """Executes the web scrapping process"""
        try:
            await self._notify("web_scrapping", "in_progress")

            products_by_pn = {p["part_number"]: p for p in self._products}
            part_numbers = list(products_by_pn.keys())

            results = await webscraping(part_numbers, self._supplier)

            for content in results:
                if not isinstance(content, dict):
                    continue
                part_number = content.get("product_part_number")
                if not part_number:
                    continue

                product = products_by_pn.get(part_number)

                if product is None:
                    continue

                if product["part_number"] == part_number:
                    product["manufacturer"] = content.get("manufacturer") or "N/A"
                    product["manufacturer_desc"] = content.get("description") or "N/A"

            await self._notify("web_scrapping", "success")
        except Exception as e:
            logger.error(f"Error to executes the webscrapping: {e}")
            await self._notify("web_scrapping", "failed", error=str(e))
            raise

    async def _get_ncm(self) -> None:
        """Executes get ncm based on descriptions"""
        try:
            await self._notify("get_ncms", "in_progress")

            query_list = []

            tasks = [setup.get_ncm(query) for query in query_list]
            ncms = await asyncio.gather(*tasks)

            await self._notify("get_ncms", "success", data=ncms)

        except Exception as e:
            logger.error(f"Error to get ncms: {e}")
            await self._notify("get_ncms", "failed", error=str(e))
            raise

    async def _get_final_description(self) -> None:
        """Executes the final description generate process"""
        try:
            await self._notify("description_generate", "in_progress")

            descs_list = [
                {
                    "name": p.get("name", ""),
                    "manufacturer_desc": p.get("manufacturer_desc", ""),
                }
                for p in self._products
            ]

            tasks = [
                Generate_final_desc.generate_final_desc_async(
                    {d["name"]: d["name"]}, d["manufacturer_desc"]
                )
                for d in descs_list
            ]

            results = await asyncio.gather(*tasks)

            for i, final_desc in enumerate(results):
                self._products[i]["final_description"] = final_desc[
                    self._products[i]["name"]
                ]

            await self._notify("description_generate", "success")
        except Exception as e:
            logger.error("Erro to generate final descriptions by LLM {e}")
            await self._notify("description_generate", "failed", error=str(e))
            raise

    async def save_data(self) -> None:
        try:
            new_supplier = await self._supplier_repo.save(
                SupplierCreate(name=self._supplier)
            )
            new_order = await self._order_repo.save(
                OrderCreate(order_date=self._order_date)
            )

            manufacturer_cache: Dict[str, int] = {}

            tasks = []

            for product in self._products:
                manufacturer_name = product.get("manufacturer") or "NÃO ENCONTRADO"

                async def save_product_data(prod=product, manuf=manufacturer_name):
                    new_product = await self._product_repo.save(
                        ProductCreate(
                            final_description=prod["final_description"],
                            erp_code=prod["erp_code"],
                        )
                    )

                    if manuf not in manufacturer_cache:
                        new_manufacturer = await self._manufacturer_repo.save(
                            ManufacturerCreate(name=manufacturer_name)
                        )
                        manufacturer_cache[manuf] = new_manufacturer.id

                    manufacturer_id = manufacturer_cache[manufacturer_name]

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
                            manufacturer_id=manufacturer_id,
                            supplier_product_id=new_supplier_product.id,
                        )
                    )

                tasks.append(save_product_data())

            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Error to save data on database: {e}")
            await self._notify("save_on_database", "failed", error=str(e))
            raise

    async def run(self) -> None:
        try:
            await self._notify("pipeline_overall", "started")
            await self._pdf_step()
            await self._web_scrapping()
            await self._get_ncm()
            await self._get_final_description()
            await self.save_data()
            await self._notify("pipeline_overall", "finished")
        except Exception as e:
            await self._notify("pipeline_overall", "failed", e)
            raise
