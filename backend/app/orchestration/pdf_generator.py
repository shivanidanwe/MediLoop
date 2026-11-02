"""
MediLoop Multi-Agent Orchestration Layer - PDF Purchase Order Generator.
Generates clean, professional Supplier Purchase Order PDFs using ReportLab.
Includes pharmacy header, PO details, itemized table of ordered medicines,
pricing breakdown, and pharmacist authorization block.
"""
import os
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

logger = logging.getLogger(__name__)


def generate_purchase_order_pdf(
    po_number: str,
    pharmacy_name: str,
    pharmacy_address: str,
    supplier_name: str,
    supplier_email: str,
    supplier_phone: str,
    items: List[Dict[str, Any]],
    subtotal: float,
    tax_amount: float,
    total_amount: float,
    output_dir: Optional[str] = None
) -> str:
    """
    Generates a formal PDF document for a supplier purchase order.
    Returns the absolute file path to the generated PDF.
    """
    if not output_dir:
        output_dir = os.path.join(os.getcwd(), "backend", "uploads", "procurement")
    os.makedirs(output_dir, exist_ok=True)

    pdf_filename = f"{po_number}.pdf"
    pdf_path = os.path.join(output_dir, pdf_filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E3A8A')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#4B5563')
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1F2937')
    )
    cell_style = ParagraphStyle(
        'CellText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12
    )
    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12
    )

    story = []

    # 1. Header Banner
    header_data = [
        [
            Paragraph("<b>MEDILOOP PHARMACY SYSTEM</b><br/><font color='#6B7280'>Automated Multi-Agent Procurement</font>", title_style),
            Paragraph(f"<b>PURCHASE ORDER</b><br/><b>PO #:</b> {po_number}<br/><b>Date:</b> {datetime.now().strftime('%d-%b-%Y')}", subtitle_style)
        ]
    ]
    header_table = Table(header_data, colWidths=[330, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT')
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1E3A8A'), spaceAfter=15))

    # 2. Pharmacy & Supplier Information
    info_data = [
        [
            Paragraph("<b>BUYER (PHARMACY):</b>", cell_bold),
            Paragraph("<b>VENDOR / DISTRIBUTOR:</b>", cell_bold)
        ],
        [
            Paragraph(f"<b>{pharmacy_name}</b><br/>{pharmacy_address}<br/>GSTIN: 27AABCM8821Q1ZG<br/>DL: MH-PUN-2022-8812", cell_style),
            Paragraph(f"<b>{supplier_name}</b><br/>Email: {supplier_email}<br/>Phone: {supplier_phone}<br/>Payment Terms: Net 30 Days", cell_style)
        ]
    ]
    info_table = Table(info_data, colWidths=[265, 265])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F3F4F6')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#D1D5DB')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 15))

    # 3. Itemized Products Table
    story.append(Paragraph("ORDERED PHARMACEUTICAL SUPPLIES", section_heading))
    story.append(Spacer(1, 6))

    table_rows = [
        [
            Paragraph("<b>#</b>", cell_bold),
            Paragraph("<b>Medicine Description</b>", cell_bold),
            Paragraph("<b>Batch / Form</b>", cell_bold),
            Paragraph("<b>Order Qty</b>", cell_bold),
            Paragraph("<b>Unit Wholesale (₹)</b>", cell_bold),
            Paragraph("<b>Line Total (₹)</b>", cell_bold)
        ]
    ]

    for idx, itm in enumerate(items, 1):
        name = itm.get("medicine_name") or itm.get("name") or "Medicine"
        strength = itm.get("strength") or ""
        desc = f"<b>{name}</b> {strength}".strip()
        form = itm.get("form") or "Strip / Box"
        qty = itm.get("quantity") or itm.get("reorder_qty") or 0
        unit_price = float(itm.get("unit_price") or itm.get("wholesale_price") or 0.0)
        line_total = float(itm.get("line_total") or (qty * unit_price))

        table_rows.append([
            Paragraph(str(idx), cell_style),
            Paragraph(desc, cell_style),
            Paragraph(form, cell_style),
            Paragraph(str(qty), cell_style),
            Paragraph(f"₹{unit_price:.2f}", cell_style),
            Paragraph(f"₹{line_total:.2f}", cell_style)
        ])

    items_table = Table(table_rows, colWidths=[25, 200, 85, 60, 80, 80])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')])
    ]))
    story.append(items_table)
    story.append(Spacer(1, 10))

    # 4. Financial Totals Table
    totals_data = [
        [Paragraph("Subtotal:", cell_bold), Paragraph(f"₹{subtotal:.2f}", cell_bold)],
        [Paragraph("GST / Taxes (12%):", cell_style), Paragraph(f"₹{tax_amount:.2f}", cell_style)],
        [Paragraph("<b>Grand Total:</b>", cell_bold), Paragraph(f"<b>₹{total_amount:.2f}</b>", cell_bold)]
    ]
    totals_table = Table(totals_data, colWidths=[450, 80])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('PADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (0, 2), (-1, 2), 1, colors.HexColor('#1E3A8A'))
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 25))

    # 5. Pharmacist Authorization Block
    auth_data = [
        [
            Paragraph("<b>Generated By:</b> MediLoop Autonomous Procurement Agent", cell_style),
            Paragraph("<b>Authorized Pharmacist Signature:</b>", cell_bold)
        ],
        [
            Paragraph("Status: AWAITING_PHARMACIST_APPROVAL", cell_style),
            Paragraph("___________________________________<br/>Registered Pharmacist (R.Ph)<br/>License Verified", cell_style)
        ]
    ]
    auth_table = Table(auth_data, colWidths=[265, 265])
    auth_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 4)
    ]))
    story.append(auth_table)

    try:
        doc.build(story)
        logger.info(f"Generated Purchase Order PDF: {pdf_path}")
        return pdf_path
    except Exception as e:
        logger.error(f"Failed to generate PO PDF: {e}")
        raise
