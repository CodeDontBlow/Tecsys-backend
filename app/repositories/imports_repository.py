# Third-party imports
from typing import List, Optional, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, update
# Local imports
from app.model.imports import Imports
from app.repositories.repository_interface import RepositoryInterface
from app.schemas.imports import ImportCreate, ImportUpdate
from app.model.supplier_product import SupplierProduct
from app.model.order import Order

from app.model.manufacturer import Manufacturer
from app.model.product import Product
from app.model.supplier import Supplier


class ImportsRepository(RepositoryInterface[ImportCreate, ImportUpdate, Imports]):
    def __init__(self, db_session: AsyncSession, model: Type[Imports]):
        self._db_session = db_session
        self._model = model

    async def save(self, import_data) -> Imports:
        """Create a new import record in the database."""
        imports_dict = import_data.model_dump()

        new_import = self._model(**imports_dict)

        try:
            self._db_session.add(new_import)
            await self._db_session.commit()
            await self._db_session.refresh(new_import)
            return new_import
        except SQLAlchemyError as e:
            await self._db_session.rollback()
            raise e

    async def list_all(self) -> List[Imports]:
      """List all imports from the most recent order."""
      subq = select(func.max(Order.order_date)).scalar_subquery()
      stmt = (
      select(Imports)
      .join(Imports.order)
      .options(
          selectinload(Imports.manufacturer),
          selectinload(Imports.supplier_product).selectinload(SupplierProduct.supplier),
          selectinload(Imports.supplier_product).selectinload(SupplierProduct.product),
          selectinload(Imports.order),
      )
        .where(Order.order_date == subq)
      )
      result = await self._db_session.execute(stmt) 
      return result.scalars().all()


    async def list_by_order_id(self, order_id: int) -> List[Imports]:
      stmt = (
            select(Imports)
            .join(Imports.order)
            .options(
                selectinload(Imports.manufacturer),
                selectinload(Imports.supplier_product).selectinload(SupplierProduct.supplier),
                selectinload(Imports.supplier_product).selectinload(SupplierProduct.product),
                selectinload(Imports.order),
            )
            .where(Imports.order_id == order_id)
        )
      result = await self._db_session.execute(stmt)
      return result.scalars().all()


    async def get_by_id(self, obj_id: int) -> Optional[Imports]:
        pass

    async def update(self, obj_id: int, obj_data: ImportUpdate) -> Imports:
      stmt = (
        update(self._model)
        .where(self._model.id == obj_id)
        .values(**obj_data.model_dump(exclude_unset=True))
        .returning(self._model)
      )
      result = await self._db_session.execute(stmt)
      updated = result.scalars().first()
      if updated is None:
        return None
      await self._db_session.commit()
      await self._db_session.refresh(updated)
      return updated

    async def delete(self, obj_id: int) -> None:
        pass
    
    async def delete_by_order_id(self, order_id: int) -> None:

      stmt = select(Imports).where(Imports.order_id == order_id)
      result = await self._db_session.execute(stmt)
      imports_to_delete = result.scalars().all()

      manufacturer_ids = set()
      supplier_product_ids = set()
      product_ids = set()
      supplier_ids = set()

      for import_record in imports_to_delete:
        manufacturer_ids.add(import_record.manufacturer_id)
        supplier_product_ids.add(import_record.supplier_product_id)
      
      if supplier_product_ids:
        stmt_sp = select(SupplierProduct).where(SupplierProduct.id.in_(supplier_product_ids))
        result_sp = await self._db_session.execute(stmt_sp)
        supplier_products = result_sp.scalars().all()
        for sp in supplier_products:
          product_ids.add(sp.product_id)
          supplier_ids.add(sp.supplier_id)

      
      for import_record in imports_to_delete:
        await self._db_session.delete(import_record)
      await self._db_session.commit()

   
      for manufacturer_id in manufacturer_ids:
        stmt = select(Imports).where(Imports.manufacturer_id == manufacturer_id)
        result = await self._db_session.execute(stmt)
        if not result.scalars().first():
          manufacturer = await self._db_session.get(Manufacturer, manufacturer_id)
          if manufacturer:
            await self._db_session.delete(manufacturer)


      for supplier_product_id in supplier_product_ids:
        stmt = select(Imports).where(Imports.supplier_product_id == supplier_product_id)
        result = await self._db_session.execute(stmt)
        if not result.scalars().first():
          supplier_product = await self._db_session.get(SupplierProduct, supplier_product_id)
          if supplier_product:
            await self._db_session.delete(supplier_product)

   
      for product_id in product_ids:
        stmt = select(SupplierProduct).where(SupplierProduct.product_id == product_id)
        result = await self._db_session.execute(stmt)
        if not result.scalars().first():
          product = await self._db_session.get(Product, product_id)
          if product:
            await self._db_session.delete(product)

      for supplier_id in supplier_ids:
        stmt = select(SupplierProduct).where(SupplierProduct.supplier_id == supplier_id)
        result = await self._db_session.execute(stmt)
        if not result.scalars().first():
          supplier = await self._db_session.get(Supplier, supplier_id)
          if supplier:
            await self._db_session.delete(supplier)

      order = await self._db_session.get(Order, order_id)
      if order:
          await self._db_session.delete(order)
      await self._db_session.commit()
