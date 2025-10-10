from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = 'f2a0df2cacf3'
down_revision: Union[str, Sequence[str], None] = '33c44889bd20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. DROP da FK em 'imports' e Renomeação da Coluna 'imports.supplyer_product_id'
    op.drop_constraint(op.f('imports_supplyer_product_id_fkey'), 'imports', type_='foreignkey')
    op.alter_column('imports', 'supplyer_product_id', new_column_name='supplier_product_id', existing_type=sa.Integer, existing_nullable=False)

    # 2. Renomeação da Tabela principal
    op.rename_table("supplyer_products", "supplier_products")

    # 3. Renomeação da COLUNA 'supplier_products.supplyer_id'
    op.alter_column('supplier_products', 'supplyer_id', new_column_name='supplier_id', existing_type=sa.Integer, existing_nullable=False)
    
    # 4. Renomeação das Restrições (de supplyer_products_... para supplier_products_...)
    # PKEY: supplyer_products_pkey -> supplier_products_pkey
    op.execute(text("ALTER TABLE supplier_products RENAME CONSTRAINT supplyer_products_pkey TO supplier_products_pkey"))
    
    # FK para 'products.id': supplyer_products_product_id_fkey -> supplier_products_product_id_fkey
    op.execute(text("ALTER TABLE supplier_products RENAME CONSTRAINT supplyer_products_product_id_fkey TO supplier_products_product_id_fkey"))
    
    # FK para 'suppliers.id': supplyer_products_supplyer_id_fkey -> supplier_products_supplier_id_fkey
    op.execute(text("ALTER TABLE supplier_products RENAME CONSTRAINT supplyer_products_supplyer_id_fkey TO supplier_products_supplier_id_fkey"))
    
    # 5. Recriação da FK em 'imports'
    op.create_foreign_key(op.f('imports_supplier_product_id_fkey'), 'imports', 'supplier_products', ['supplier_product_id'], ['id'])


def downgrade() -> None:
    # 1. Remover a FK em 'imports'
    op.drop_constraint(op.f('imports_supplier_product_id_fkey'), 'imports', type_='foreignkey')

    # 2. Renomear as restrições de volta (de supplier_products_... para supplyer_products_...)
    op.execute(text("ALTER TABLE supplier_products RENAME CONSTRAINT supplier_products_pkey TO supplyer_products_pkey"))
    op.execute(text("ALTER TABLE supplier_products RENAME CONSTRAINT supplier_products_product_id_fkey TO supplyer_products_product_id_fkey"))
    op.execute(text("ALTER TABLE supplier_products RENAME CONSTRAINT supplier_products_supplier_id_fkey TO supplyer_products_supplyer_id_fkey"))
    
    # 3. Renomeação da Coluna 'supplier_products.supplier_id' de volta
    op.alter_column('supplier_products', 'supplier_id', new_column_name='supplyer_id', existing_type=sa.INTEGER, existing_nullable=False)

    # 4. Renomeação da Tabela
    op.rename_table("supplier_products", "supplyer_products")
    
    # 5. Renomeação da Coluna 'imports.supplier_product_id' e Recriação da FK
    op.alter_column('imports', 'supplier_product_id', new_column_name='supplyer_product_id', existing_type=sa.INTEGER, existing_nullable=False)
    op.create_foreign_key(op.f('imports_supplyer_product_id_fkey'), 'imports', 'supplyer_products', ['supplyer_product_id'], ['id'])