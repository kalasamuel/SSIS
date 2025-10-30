from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

def generate_purchase_order_pdf(purchase_order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, f"Purchase Order - #{purchase_order.id}")
    y -= 30

    p.setFont("Helvetica", 12)
    p.drawString(50, y, f"Supplier: {purchase_order.supplier.supplier_name}")
    y -= 20
    p.drawString(50, y, f"Address: {purchase_order.supplier.address or '-'}")
    y -= 20
    p.drawString(50, y, f"Email: {purchase_order.supplier.email or '-'}")
    y -= 30

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Product Details")
    y -= 20
    p.setFont("Helvetica", 12)
    p.drawString(50, y, "Name")
    p.drawString(350, y, "Qty")
    p.drawString(400, y, "Unit Cost")
    p.drawString(500, y, "Subtotal")
    y -= 20

    total = 0
    for item in purchase_order.items.all():
        line_total = item.quantity_ordered * item.unit_cost
        total += line_total
        p.drawString(50, y, item.product.product_name)
        p.drawString(350, y, str(item.quantity_ordered))
        p.drawString(400, y, str(item.unit_cost))
        p.drawString(500, y, str(line_total))
        y -= 20

    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(400, y, f"Total: UGX {total:,.2f}")

    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
