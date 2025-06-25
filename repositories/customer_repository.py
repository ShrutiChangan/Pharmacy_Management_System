from database.connection import DatabaseConnection

class CustomerRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_all_customers(self):
        query = "SELECT * FROM customers"
        self.db.execute_query(query)
        return self.db.fetch_all()

    def search_customers(self, search_term):
        query = """
        SELECT * FROM customers 
        WHERE customer_id LIKE %s OR name LIKE %s OR contact LIKE %s
        """
        params = (f"%{search_term}%", f"%{search_term}%", f"%{search_term}%")
        self.db.execute_query(query, params)
        return self.db.fetch_all()

    def get_customer_by_id(self, customer_id):
        query = "SELECT * FROM customers WHERE customer_id = %s"
        self.db.execute_query(query, (customer_id,))
        return self.db.fetch_one()

    def add_customer(self, customer_data):
        query = """
        INSERT INTO customers (customer_id, name, contact, email, address)
        VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            customer_data['customer_id'],
            customer_data['name'],
            customer_data['contact'],
            customer_data['email'],
            customer_data['address']
        )

        success = self.db.execute_query(query, params)
        if success:
            self.db.commit()
        return success

    def update_customer(self, customer_data):
        query = """
        UPDATE customers
        SET name = %s, contact = %s, email = %s, address = %s
        WHERE customer_id = %s
        """
        params = (
            customer_data['name'],
            customer_data['contact'],
            customer_data['email'],
            customer_data['address'],
            customer_data['customer_id']
        )

        success = self.db.execute_query(query, params)
        if success:
            self.db.commit()
        return success

    def delete_customer(self, customer_id):
        query = "DELETE FROM customers WHERE customer_id = %s"
        success = self.db.execute_query(query, (customer_id,))
        if success:
            self.db.commit()
        return success