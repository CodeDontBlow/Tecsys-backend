import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.libs.ncm import setup
from app.libs.websocket.manager import ws_manager
from app.model.imports import Imports
from app.model.order import Order
from app.model.product import Product
from app.model.supplier import Supplier
from app.model.supplier_product import SupplierProduct
from app.repositories.imports_repository import ImportsRepository
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.supplier_product_repository import SupplierProductRepository
from app.repositories.supplier_repository import SupplierRepository
from app.schemas.imports import ImportCreate
from app.schemas.order import OrderCreate
from app.schemas.product import ProductCreate
from app.schemas.supplier import SupplierCreate
from app.schemas.supplier_product import SupplierProductCreate
from app.services.extract_service.enterPDF import EnterPDF
from app.services.extract_service.extract_json import Extract_json

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

    async def _notify(self, process: str, status: str, error=None) -> dict:
        payload = {"process": process, "status": status, "error": error}

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
        """Executes the web scrapping based on part numbers"""
        await self._notify("web_scrapping", "in_progress")
        part_numbers = [product["part_number"] for product in self._products]
        print("webscraping executado")
        await self._notify("web_scrapping", "success")

    async def _get_ncm(self) -> None:
        """Executes get ncm based on descriptions"""
        await self._notify("get_ncms", "in_progress")

        query = "LED Verde, 2 mm SMD"

        self._ncm_founded = await setup.get_ncm(query)

        await self._notify("get_ncms", "success")

    async def _get_final_description(self) -> None:
        """Executes the final description generate"""
        await self._notify("product_description", "in_progress")

        print("gerou descrição final")
        await self._notify("product_description", "success")

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
                    ProductCreate(final_description="descrição " + str(counter))
                )
                counter += 1

                print("new_product", new_product)

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
            await self._notify("process_pipeline", "started")
            await self._pdf_step()
            await self._web_scrapping()
            await self._get_ncm()
            await self._get_final_description()
            await self.save_data()
            print(self._supplier)
            await self._notify("process_overall", "finished")
        except Exception as e:
            await self._notify("pipeline_overall", "failed", e)
            raise
