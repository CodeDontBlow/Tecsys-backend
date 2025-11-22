from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from typing import List
from sqlalchemy import select
import io

from openpyxl import Workbook

from app.core.dependencies import DatabaseDependency
from app.model import Product, SupplierProduct, Imports, Manufacturer

router = APIRouter()


@router.get("/export")
async def export_items(
    db: DatabaseDependency,
    format: str = Query("json", description="json|csv|excel"),
    download: bool = Query(False, description="Se true retorna um arquivo .xlsx para download"),
):
    """Returns records and creates a CSV file in the requested format.

        The CSV uses `;` as a separator, and the first line is the header:

        series;erp code; system description; description for import declaration; ncm; manufacturer;

        Each line contains (per product/import):

        id;erp_code;erp_description+product_part_number;final_description+product_part_number+erp_code;ncm;manufacturer

    """

    # Creates a select statement with joins: product -> supplier_product -> imports -> manufacturer
    stmt = (
        select(
            Product.erp_code,
            SupplierProduct.erp_description,
            Product.final_description,
            Imports.product_part_number,
            Product.ncm,
            Manufacturer.name.label("manufacturer"),
        )
        .join(SupplierProduct, Product.id == SupplierProduct.product_id)
        .join(Imports, SupplierProduct.id == Imports.supplier_product_id)
        .join(Manufacturer, Imports.manufacturer_id == Manufacturer.id)
    )

    result = await db.execute(stmt)
    rows = result.all()

    data: List[dict] = []
    csv_lines: List[str] = []

    csv_lines.append(
        "série;codigo erp; descrição no sistema; descrição para di; ncm; fabricante;"
    )

    for idx, (erp_code, erp_description, final_description, part_number, ncm, manufacturer) in enumerate(rows, start=1):
        row = {
            "erp_code": erp_code,
            "erp_description": erp_description,
            "final_description": final_description,
            "product_part_number": part_number,
            "ncm": ncm,
            "manufacturer": manufacturer,
        }
        data.append(row)

        col_erp_desc_plus_part = f"{erp_description} PN: {part_number}"
        col_final_plus_part_erp = f"{final_description} PN: {part_number} (COD:{erp_code})"

        csv_line = (
            f"{idx};{erp_code};{col_erp_desc_plus_part};{col_final_plus_part_erp};{ncm};{manufacturer};"
        )
        csv_lines.append(csv_line)

    csv_text = "\n".join(csv_lines)

    if download:
        wb = Workbook()
        ws = wb.active
        header = [
            "série",
            "codigo erp",
            "descrição no sistema",
            "descrição para di",
            "ncm",
            "fabricante",
        ]
        ws.append(header)

        for idx, row in enumerate(data, start=1):
            erp_code = row.get("erp_code") or ""
            erp_description = row.get("erp_description") or ""
            final_description = row.get("final_description") or ""
            part_number = row.get("product_part_number") or ""
            ncm = row.get("ncm") or ""
            manufacturer = row.get("manufacturer") or ""

            col_erp_desc_plus_part = f"{erp_description}+{part_number}"
            col_final_plus_part_erp = f"{final_description}+{part_number}+{erp_code}"

            ws.append([
                idx,
                erp_code,
                col_erp_desc_plus_part,
                col_final_plus_part_erp,
                ncm,
                manufacturer,
            ])

        stream = io.BytesIO()
        wb.save(stream)
        stream.seek(0)
        filename = "export.xlsx"
        return StreamingResponse(
            stream,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
        )

    fmt = (format or "json").lower()
    if fmt in ("csv", "excel"):
        csv_bytes = csv_text.encode("utf-8-sig")
        buffer = io.BytesIO(csv_bytes)
        filename = "export.csv"
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=\"{filename}\""},
        )

    return {"data": data, "csv": csv_text}
