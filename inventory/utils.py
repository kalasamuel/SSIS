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
    p.drawString(50, y, f"Supplier: {purchase_order.supplier.name}")
    y -= 20
    p.drawString(50, y, f"Address: {purchase_order.supplier.address or '-'}")
    y -= 20
    p.drawString(50, y, f"Contact: {purchase_order.supplier.contact_person or '-'}")
    y -= 20
    p.drawString(50, y, f"Email: {purchase_order.supplier.contact_email or '-'}")
    y -= 30

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "Product Details")
    y -= 20
    p.setFont("Helvetica", 12)
    p.drawString(50, y, "Name")
    p.drawString(250, y, "SKU")
    p.drawString(350, y, "Qty")
    p.drawString(400, y, "Unit Cost")
    p.drawString(500, y, "Subtotal")
    y -= 20

    for item in purchase_order.items.all():
        p.drawString(50, y, item.product.name)
        p.drawString(250, y, item.product.sku)
        p.drawString(350, y, str(item.quantity))
        p.drawString(400, y, str(item.unit_cost))
        p.drawString(500, y, str(item.subtotal))
        y -= 20

    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(400, y, f"Total: UGX {purchase_order.total_cost:,.2f}")

    p.showPage()
    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf
