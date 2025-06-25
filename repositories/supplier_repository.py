from database.connection import DatabaseConnection
from repositories.medicine_repository import MedicineRepository

class SupplierRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_suppliers(self):
        query = "SELECT * FROM suppliers"
        self.db.execute_query(query)
        return self.db.fetch_all()

    def search_suppliers(self, search_by, search_term):
        query = "SELECT * FROM suppliers WHERE "

        if search_by == 'ID':
            query += "supplier_id LIKE %s"
        elif search_by == 'Name':
            query += "name LIKE %s"
        elif search_by == 'Contact No':
            query += "contact LIKE %s"

        self.db.execute_query(query, (f"%{search_term}%",))
        return self.db.fetch_all()

    def get_supplier_by_id(self, supplier_id):
        query = "SELECT * FROM suppliers WHERE supplier_id = %s"
        self.db.execute_query(query, (supplier_id,))
        return self.db.fetch_one()

    def add_supplier(self, supplier_data):
        query = """
        INSERT INTO suppliers (supplier_id, name, contact, email, address)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            supplier_data['supplier_id'],
            supplier_data['name'],
            supplier_data['contact'],
            supplier_data['email'],
            supplier_data['address']
        )

        success = self.db.execute_query(query, params)
        if success:
            self.db.commit()
        return success

    def update_supplier(self, supplier_data):
        query = """
        UPDATE suppliers
        SET name = %s, contact = %s, email = %s, address = %s
        WHERE supplier_id = %s
        """
        params = (
            supplier_data['name'],
            supplier_data['contact'],
            supplier_data['email'],
            supplier_data['address'],
            supplier_data['supplier_id']
        )

        success = self.db.execute_query(query, params)
        if success:
            self.db.commit()
        return success

    def delete_supplier(self, supplier_id):
        query = "DELETE FROM suppliers WHERE supplier_id = %s"
        success = self.db.execute_query(query, (supplier_id,))
        if success:
            self.db.commit()
        return success

    def add_supply_record(self, supply_data):
        query = """
        INSERT INTO supplies (supplier_id, medicine_id, quantity, amount, supply_date)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            supply_data['supplier_id'],
            supply_data['medicine_id'],
            supply_data['quantity'],
            supply_data['amount'],
            supply_data['supply_date']
        )

        success = self.db.execute_query(query, params)
        if success:
            self.db.commit()

            # Update medicine quantity
            medicine_repo = MedicineRepository(self.db)
            medicine_repo.update_quantity(supply_data['medicine_id'], supply_data['quantity'])

        return success

    def get_supply_records(self, supplier_id=None, from_date=None, to_date=None):
        query = """
        SELECT s.supply_id, sup.supplier_id, sup.name as supplier_name, 
               m.medicine_id, m.name as medicine_name, s.quantity, 
               s.amount, s.supply_date
        FROM supplies s
        JOIN suppliers sup ON s.supplier_id = sup.supplier_id
        JOIN medicines m ON s.medicine_id = m.medicine_id
        WHERE 1=1
        """

        params = []

        if supplier_id and supplier_id != "All Suppliers":
            query += " AND sup.supplier_id = %s"
            params.append(supplier_id)

        if from_date:
            query += " AND s.supply_date >= %s"
            params.append(from_date)

        if to_date:
            query += " AND s.supply_date <= %s"
            params.append(to_date)

        query += " ORDER BY s.supply_date DESC"

        self.db.execute_query(query, tuple(params) if params else None)
        return self.db.fetch_all()