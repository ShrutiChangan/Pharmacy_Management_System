from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet , ParagraphStyle
from reportlab.lib.units import inch
import os

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'Title',
            parent=self.styles['Heading1'],
            fontSize=16,
            alignment=1,
            spaceAfter=20
        )
        self.header_style = ParagraphStyle(
            'Header',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=10
        )
        self.normal_style = self.styles['Normal']

    def generate_bill_pdf(self, bill_data, filename):
        try:
            doc = SimpleDocTemplate(
                filename,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )

            elements = []

            # Title
            elements.append(Paragraph("Pharmacy Management System", self.title_style))
            elements.append(Paragraph("INVOICE", self.title_style))
            elements.append(Spacer(1, 0.25 * inch))

            # Customer and Bill Info
            customer_info = [
                ["Customer Information", "Bill Information"],
                [f"Name: {bill_data['customer_name']}", f"Bill No: {bill_data['bill_id']}"],
                [f"Contact: {bill_data['customer_contact']}", f"Date: {bill_data['date']}"],
                [f"Address: {bill_data['customer_address']}", ""]
            ]

            customer_table = Table(customer_info, colWidths=[3 * inch, 3 * inch])
            customer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
                ('ALIGN', (0, 0), (1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (1, 0), 12),
                ('BACKGROUND', (0, 1), (1, -1), colors.white),
                ('GRID', (0, 0), (1, -1), 1, colors.black)
            ]))

            elements.append(customer_table)
            elements.append(Spacer(1, 0.25 * inch))

            # Items Table - Removed Medicine ID column
            elements.append(Paragraph("Items", self.header_style))

            # Table header without Medicine ID
            items_data = [["S.No.", "Medicine Name", "Quantity", "Price (₹)", "Amount (₹)"]]

            # Add items without Medicine ID
            for i, item in enumerate(bill_data['items'], 1):
                items_data.append([
                    str(i),
                    item['medicine_name'],
                    item['quantity'],
                    item['price'],
                    item['amount']
                ])

            # Add totals
            items_data.append(["", "", "", "Subtotal:", bill_data['subtotal']])
            items_data.append(["", "", "", "Tax (18%):", bill_data['tax']])
            items_data.append(["", "", "", "Total:", bill_data['total']])

            # Adjusted column widths since we removed one column
            items_table = Table(items_data, colWidths=[0.5 * inch, 2.5 * inch, 0.75 * inch, 1 * inch, 1 * inch])
            items_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (4, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (4, 0), colors.black),
                ('ALIGN', (0, 0), (4, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (4, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (4, 0), 12),
                ('BACKGROUND', (0, 1), (4, -4), colors.white),
                ('GRID', (0, 0), (4, -4), 1, colors.black),
                ('ALIGN', (3, -3), (4, -1), 'RIGHT'),
                ('FONTNAME', (3, -3), (4, -1), 'Helvetica-Bold'),
                ('LINEABOVE', (3, -3), (4, -3), 1, colors.black),
                ('LINEABOVE', (3, -1), (4, -1), 1, colors.black),
                ('LINEBELOW', (3, -1), (4, -1), 1, colors.black)
            ]))

            elements.append(items_table)
            elements.append(Spacer(1, 0.5 * inch))

            # Footer
            elements.append(Paragraph("Thank you for your business!", self.header_style))
            elements.append(Paragraph("Terms & Conditions Apply", self.normal_style))

            doc.build(elements)
            return True

        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False