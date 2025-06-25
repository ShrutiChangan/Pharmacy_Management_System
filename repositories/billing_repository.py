from database.connection import DatabaseConnection
from tkinter import messagebox
import mysql.connector
from mysql.connector import Error

class BillingRepository:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def create_bill(self, bill_data):
        # Start a transaction
        try:
            # Insert bill header
            bill_query = """
            INSERT INTO bills (bill_id, customer_id, bill_date, subtotal, tax, total)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            bill_params = (
                bill_data['bill_id'],
                bill_data['customer_id'],
                bill_data['date'],
                bill_data['subtotal'],
                bill_data['tax'],
                bill_data['total']
            )

            self.db.execute_query(bill_query, bill_params)

            # Insert bill items
            for item in bill_data['items']:
                item_query = """
                INSERT INTO bill_items (bill_id, medicine_id, quantity, price, amount)
                VALUES (%s, %s, %s, %s, %s)
                """
                item_params = (
                    bill_data['bill_id'],
                    item['medicine_id'],
                    item['quantity'],
                    item['price'],
                    item['amount']
                )

                self.db.execute_query(item_query, item_params)

                # Update medicine quantity
                update_query = """
                UPDATE medicines
                SET quantity = quantity - %s
                WHERE medicine_id = %s
                """
                update_params = (item['quantity'], item['medicine_id'])

                self.db.execute_query(update_query, update_params)

            # Commit the transaction
            self.db.commit()
            return True

        except Error as e:
            # Rollback in case of error
            self.db.rollback()
            messagebox.showerror("Billing Error", f"Error creating bill: {e}")
            return False

    def get_all_bills(self):
        query = """
        SELECT b.bill_id, b.customer_id, c.name as customer_name, 
               b.total, b.bill_date,
               GROUP_CONCAT(m.name SEPARATOR ', ') as medicines
        FROM bills b
        JOIN customers c ON b.customer_id = c.customer_id
        JOIN bill_items bi ON b.bill_id = bi.bill_id
        JOIN medicines m ON bi.medicine_id = m.medicine_id
        GROUP BY b.bill_id, b.customer_id, c.name, b.total, b.bill_date
        ORDER BY b.bill_date DESC
        """
        self.db.execute_query(query)
        return self.db.fetch_all()

    def search_bills(self, search_by, search_term):
        query = """
        SELECT b.bill_id, b.customer_id, c.name as customer_name, 
               b.total, b.bill_date,
               GROUP_CONCAT(m.name SEPARATOR ', ') as medicines
        FROM bills b
        JOIN customers c ON b.customer_id = c.customer_id
        JOIN bill_items bi ON b.bill_id = bi.bill_id
        JOIN medicines m ON bi.medicine_id = m.medicine_id
        WHERE 
        """

        if search_by == 'Bill ID':
            query += "b.bill_id LIKE %s"
        elif search_by == 'Customer Name':
            query += "c.name LIKE %s"
        elif search_by == 'Customer ID':
            query += "b.customer_id LIKE %s"
        elif search_by == 'Date':
            query += "b.bill_date LIKE %s"

        query += " GROUP BY b.bill_id, b.customer_id, c.name, b.total, b.bill_date"
        query += " ORDER BY b.bill_date DESC"

        self.db.execute_query(query, (f"%{search_term}%",))
        return self.db.fetch_all()

    def filter_bills_by_date(self, from_date, to_date):
        query = """
        SELECT b.bill_id, b.customer_id, c.name as customer_name, 
               b.total, b.bill_date,
               GROUP_CONCAT(m.name SEPARATOR ', ') as medicines
        FROM bills b
        JOIN customers c ON b.customer_id = c.customer_id
        JOIN bill_items bi ON b.bill_id = bi.bill_id
        JOIN medicines m ON bi.medicine_id = m.medicine_id
        WHERE b.bill_date BETWEEN %s AND %s
        GROUP BY b.bill_id, b.customer_id, c.name, b.total, b.bill_date
        ORDER BY b.bill_date DESC
        """

        self.db.execute_query(query, (from_date, to_date))
        return self.db.fetch_all()

    def get_bill_details(self, bill_id):
        # Get bill header
        header_query = """
        SELECT b.*, c.name as customer_name, c.contact as customer_contact, 
               c.email as customer_email, c.address as customer_address
        FROM bills b
        JOIN customers c ON b.customer_id = c.customer_id
        WHERE b.bill_id = %s
        """

        self.db.execute_query(header_query, (bill_id,))
        bill_header = self.db.fetch_one()

        if not bill_header:
            return None

        # Get bill items
        items_query = """
        SELECT bi.*, m.name as medicine_name
        FROM bill_items bi
        JOIN medicines m ON bi.medicine_id = m.medicine_id
        WHERE bi.bill_id = %s
        """

        self.db.execute_query(items_query, (bill_id,))
        bill_items = self.db.fetch_all()

        # Combine header and items
        bill_details = {
            'bill_id': bill_header['bill_id'],
            'customer_id': bill_header['customer_id'],
            'customer_name': bill_header['customer_name'],
            'customer_contact': bill_header['customer_contact'],
            'customer_address': bill_header['customer_address'],
            'date': bill_header['bill_date'].strftime('%d-%m-%Y'),
            'subtotal': str(bill_header['subtotal']),
            'tax': str(bill_header['tax']),
            'total': str(bill_header['total']),
            'items': []
        }

        for item in bill_items:
            bill_details['items'].append({
                'medicine_id': item['medicine_id'],
                'medicine_name': item['medicine_name'],
                'quantity': str(item['quantity']),
                'price': str(item['price']),
                'amount': str(item['amount'])
            })

        return bill_details
    
    def get_all_bill_items(self):
        try:
            query = "SELECT * FROM bill_items"
            self.db.execute_query(query)
            return self.db.fetch_all()
        except Exception as e:
            print("Error fetching bill items:", e)
            return []

        
    def get_best_sellers(self, limit=10):
        query = """
            SELECT m.name AS medicine_name, SUM(bi.quantity) AS total_quantity_sold
            FROM bill_items bi
            JOIN medicines m ON bi.medicine_id = m.medicine_id
            GROUP BY bi.medicine_id
            ORDER BY total_quantity_sold DESC
            LIMIT %s
        """
        try:
            self.db.execute_query(query, (limit,))
            return self.db.fetch_all()
        except Exception as e:
            print("Error fetching best sellers:", e)
            return []