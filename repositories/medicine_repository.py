from database.connection import DatabaseConnection
from tkinter import messagebox

class MedicineRepository:
    def __init__(self, db_connection):
        self.db = db_connection
        self.suppliers = []  # Cache for suppliers
        self.load_suppliers()  # Initial load

    def load_suppliers(self):
        """Load or refresh the list of suppliers"""
        query = "SELECT * FROM suppliers"
        self.db.execute_query(query)
        self.suppliers = self.db.fetch_all()

    def get_supplier_names(self):
        """Return list of supplier names"""
        return [supplier['name'] for supplier in self.suppliers]

    def get_all_medicines(self):
        query = """
        SELECT m.medicine_id, m.name, s.name as supplier_name, m.price, m.quantity, 
               m.expiry_date, m.location
        FROM medicines m
        LEFT JOIN suppliers s ON m.supplier_id = s.supplier_id
        """
        self.db.execute_query(query)
        return self.db.fetch_all()

    def search_medicines(self, search_by, search_term):
        query = """
        SELECT m.medicine_id, m.name, s.name as supplier_name, m.price, m.quantity, 
               m.expiry_date, m.location
        FROM medicines m
        LEFT JOIN suppliers s ON m.supplier_id = s.supplier_id
        WHERE 
        """

        if search_by == 'ID':
            query += "m.medicine_id LIKE %s"
        elif search_by == 'Name':
            query += "m.name LIKE %s"
        elif search_by == 'Supplier':
            query += "s.name LIKE %s"
        elif search_by == 'Location':
            query += "m.location LIKE %s"
        else:
            return []  # Invalid search type

        self.db.execute_query(query, (f"%{search_term}%",))
        return self.db.fetch_all()

    def get_medicine_by_id(self, medicine_id):
        query = """
        SELECT m.*, s.name as supplier_name
        FROM medicines m
        LEFT JOIN suppliers s ON m.supplier_id = s.supplier_id
        WHERE m.medicine_id = %s
        """
        self.db.execute_query(query, (medicine_id,))
        return self.db.fetch_one()

    def get_supplier_id_by_name(self, supplier_name):
        query = "SELECT supplier_id FROM suppliers WHERE name = %s"
        self.db.execute_query(query, (supplier_name,))
        result = self.db.fetch_one()
        return result['supplier_id'] if result else None

    def add_medicine(self, medicine_data):
        # Get supplier_id from supplier name
        supplier_id = self.get_supplier_id_by_name(medicine_data['supplier_name'])

        if not supplier_id:
            messagebox.showerror("Error", f"Supplier '{medicine_data['supplier_name']}' not found")
            return False

        query = """
        INSERT INTO medicines (medicine_id, name, description, supplier_id, price, 
                              quantity, expiry_date, location)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            medicine_data['medicine_id'],
            medicine_data['name'],
            medicine_data['description'],
            supplier_id,
            medicine_data['price'],
            medicine_data['quantity'],
            medicine_data['expiry_date'],
            medicine_data['location']
        )

        success = self.db.execute_query(query, params)
        if success:
            self.db.commit()
        return success

    def update_medicine(self, medicine_data):
        # Get supplier_id from supplier name
        supplier_id = self.get_supplier_id_by_name(medicine_data['supplier_name'])

        if not supplier_id:
            messagebox.showerror("Error", f"Supplier '{medicine_data['supplier_name']}' not found")
            return False

        query = """
        UPDATE medicines
        SET name = %s, description = %s, supplier_id = %s, price = %s, 
            quantity = %s, expiry_date = %s, location = %s
        WHERE medicine_id = %s
        """
        params = (
            medicine_data['name'],
            medicine_data['description'],
            supplier_id,
            medicine_data['price'],
            medicine_data['quantity'],
            medicine_data['expiry_date'],
            medicine_data['location'],
            medicine_data['medicine_id']
        )

        success = self.db.execute_query(query, params)
        if success:
            self.db.commit()
        return success

    def delete_medicine(self, medicine_id):
        query = "DELETE FROM medicines WHERE medicine_id = %s"
        success = self.db.execute_query(query, (medicine_id,))
        if success:
            self.db.commit()
        return success

    def update_quantity(self, medicine_id, quantity_change):
        query = """
        UPDATE medicines
        SET quantity = quantity + %s
        WHERE medicine_id = %s
        """
        success = self.db.execute_query(query, (quantity_change, medicine_id))
        if success:
            self.db.commit()
        return success

