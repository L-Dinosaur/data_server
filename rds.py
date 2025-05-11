import mysql.connector
from mysql.connector import Error

# Not in Use - DB test script

class DatabaseManager:
    def __init__(self, host='localhost', user='admin', password='admin123!', database='db_test'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.cursor = None

    def connect(self):

        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )

            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print("Successfully connected to the database")
                return True
            else:
                return False
        except Error as e:
            print(f"Error: {e}")
            return False

    def close_connection(self):

        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("Database connection closed")

    def create_record(self, table, data):

        try:
            # Prepare the SQL query
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            values = tuple(data.values())

            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

            # Execute the query
            self.cursor.execute(query, values)
            self.connection.commit()

            print(f"Record inserted into {table} successfully")
            return self.cursor.lastrowid
        except Error as e:
            print(f"Error inserting record: {e}")
            return None

    def read_records(self, table, conditions=None, limit=None):

        try:
            query = f"SELECT * FROM {table}"

            # Add WHERE clause if conditions are provided
            if conditions:
                where_clause = ' AND '.join([f"{k} = %s" for k in conditions.keys()])
                query += f" WHERE {where_clause}"
                values = list(conditions.values())
            else:
                values = None

            # Add LIMIT clause if specified
            if limit:
                query += f" LIMIT {limit}"

            # Execute the query
            if values:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)

            return self.cursor.fetchall()
        except Error as e:
            print(f"Error retrieving records: {e}")
            return None

    def update_record(self, table, updates, conditions):

        try:
            # Prepare SET and WHERE clauses
            set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
            where_clause = ' AND '.join([f"{k} = %s" for k in conditions.keys()])

            # Combine values for the query
            values = list(updates.values()) + list(conditions.values())

            query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"

            # Execute the query
            self.cursor.execute(query, values)
            self.connection.commit()

            print(f"Updated {self.cursor.rowcount} record(s) in {table}")
            return self.cursor.rowcount
        except Error as e:
            print(f"Error updating record: {e}")
            return 0

    def delete_record(self, table, conditions):

        try:
            # Prepare WHERE clause
            where_clause = ' AND '.join([f"{k} = %s" for k in conditions.keys()])
            values = tuple(conditions.values())

            query = f"DELETE FROM {table} WHERE {where_clause}"

            # Execute the query
            self.cursor.execute(query, values)
            self.connection.commit()

            print(f"Deleted {self.cursor.rowcount} record(s) from {table}")
            return self.cursor.rowcount
        except Error as e:
            print(f"Error deleting record: {e}")
            return 0

    def create_table(self, table_name, columns, primary_key=None, foreign_keys=None, unique_constraints=None,
                     if_not_exists=True):

        try:
            # Prepare column definitions
            column_definitions = [f"{col} {dtype}" for col, dtype in columns.items()]

            # Add primary key if specified
            if primary_key:
                column_definitions.append(f"PRIMARY KEY ({primary_key})")

            # Add foreign key constraints if specified
            if foreign_keys:
                for col, fk_info in foreign_keys.items():
                    fk_def = (f"FOREIGN KEY ({col}) REFERENCES {fk_info['ref_table']} "
                              f"({fk_info['ref_column']})")
                    column_definitions.append(fk_def)

            # Add unique constraints if specified
            if unique_constraints:
                unique_def = f"UNIQUE ({', '.join(unique_constraints)})"
                column_definitions.append(unique_def)

            # Construct the full CREATE TABLE query
            exists_clause = "IF NOT EXISTS " if if_not_exists else ""
            query = (f"CREATE TABLE {exists_clause}{table_name} ("
                     f"{', '.join(column_definitions)}"
                     ")")

            # Execute the query
            self.cursor.execute(query)
            self.connection.commit()

            print(f"Table {table_name} created successfully")
            return True
        except Error as e:
            print(f"Error creating table {table_name}: {e}")
            return False

    def drop_table(self, table_name, if_exists=True):

        try:
            exists_clause = "IF EXISTS " if if_exists else ""
            query = f"DROP TABLE {exists_clause}{table_name}"

            # Execute the query
            self.cursor.execute(query)
            self.connection.commit()

            print(f"Table {table_name} dropped successfully")
            return True
        except Error as e:
            print(f"Error dropping table {table_name}: {e}")
            return False


if __name__ == '__main__':
    db = DatabaseManager(
        host='rds-test.cb680qoi6cro.us-east-2.rds.amazonaws.com',
        user='admin',
        password='admin123!',
        database='rds_test'
    )

    # Connect to the database
    if db.connect():
        try:

            # Create table
            created = db.create_table('positions', columns={'ticker': 'varchar(255)', 'name': 'varchar(255)', 'unit': 'int'}, primary_key='ticker')

            # Create (Insert) a record
            new_record = {
                'ticker': 'AAPL',
                'name': 'Apple Inc'
            }
            inserted_id = db.create_record('positions', new_record)

            # Read records
            records = db.read_records('positions')
            print(records)

            # # Delete a record
            delete_conditions = {'ticker': 'AAPL'}
            db.delete_record('positions', delete_conditions)

            db.drop_table('positions')

        finally:
            db.close_connection()
