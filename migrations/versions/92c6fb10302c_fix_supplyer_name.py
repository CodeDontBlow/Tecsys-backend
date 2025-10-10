from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = '92c6fb10302c'
down_revision: Union[str, Sequence[str], None] = 'f2a0df2cacf3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Renomear a coluna 'supplyer_id' para 'supplier_id'
    op.alter_column('supplier_products', 'supplyer_id', new_column_name='supplier_id', existing_type=sa.Integer, existing_nullable=False)
    
    # 2. Renomear as restrições da tabela 'supplier_products' (SQL Puro para garantir a execução)
    # A tabela já está com o nome correto: 'supplier_products'

    # Renomear Primary Key (PKEY): supplyer_products_pkey -> supplier_products_pkey
    op.execute(text("ALTER TABLE supplier_products RENAME CONSTRAINT supplyer_products_pkey TO supplier_products_pkey"))
    
    # Renomear FK para 'product_id': supplyer_products_product_id_fkey -> supplier_products_product_id_fkey
    op.execute(text("ALTER TABLE supplier_products RENAME CONSTRAINT supplyer_products_product_id_fkey TO supplier_products_product_id_fkey"))
    
    # Renomear FK para 'supplier_id': supplyer_products_supplyer_id_fkey -> supplier_products_supplier_id_fkey
    op.execute(text("ALTER TABLE supplier_products RENAME CONSTRAINT supplyer_products_supplyer_id_fkey TO supplier_products_supplier_id_fkey"))


def downgrade() -> None:
    # 1. Renomear as restrições de volta (SQL Puro)
    
    # PKEY: supplier_products_pkey -> supplyer_products_pkey
    op.execute(text("ALTER TABLE supplier_products RENAME CONSTRAINT supplier_products_pkey TO supplyer_products_pkey"))
    
    # FK para 'product_id': supplier_products_product_id_fkey -> supplyer_products_product_id_fkey
    op.execute(text("ALTER TABLE supplier_products RENAME CONSTRAINT supplier_products_product_id_fkey TO supplyer_products_product_id_fkey"))
    
    # FK para 'supplier_id': supplier_products_supplier_id_fkey -> supplyer_products_supplyer_id_fkey
    op.execute(text("ALTER TABLE supplier_products RENAME CONSTRAINT supplier_products_supplier_id_fkey TO supplyer_products_supplyer_id_fkey"))

    # 2. Renomear a coluna 'supplier_id' de volta para 'supplyer_id'
    op.alter_column('supplier_products', 'supplier_id', new_column_name='supplyer_id', existing_type=sa.INTEGER, existing_nullable=False)