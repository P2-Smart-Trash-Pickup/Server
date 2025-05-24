import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ Create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
    
    return conn

def create_table(conn, create_table_sql):
    """ Create a table from the create_table_sql statement """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def insert_data(conn, data):
    """ Insert data into the table """
    sql = ''' INSERT INTO employees(artist_name, genre, martiness)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, data)
    conn.commit()
    return cur.lastrowid

def select_all_employees(conn):
    """ Query all rows in the employees table """
    cur = conn.cursor()
    cur.execute("SELECT * FROM employees")
    
    rows = cur.fetchall()
    
    print("\nEmployee Data:")
    print("-" * 50)
    for row in rows:
        print(row)

def main():
    database = "martinness.db"
    
    # SQL statement for creating the employees table
    sql_create_employees_table = """ CREATE TABLE IF NOT EXISTS employees (
                                        artist_id integer PRIMARY KEY,
                                        artist_name text NOT NULL,
                                        genre text NOT NULL,
                                        martiness integer NOT NULL
                                    ); """
    
    # Create a database connection
    conn = create_connection(database)
    
    if conn is not None:
        # Create the employees table
        create_table(conn, sql_create_employees_table)
        
        # Insert some employee data
        employees = [
            ("Eminem", "HipHop", 5),
            ("Masayoshi Takana","J-Pop",8),
            ("Ado","J-Pop",6),
            ("Imagine Dragons","Pop-Rock",4)
        ]
        
        for employee in employees:
            insert_data(conn, employee)
            print(f"Inserted employee: {employee[0]}")
        
        # Query and display all employees
        select_all_employees(conn)
        
        # Close the connection
        conn.close()
        print("\nDatabase connection closed.")
    else:
        print("Error! Cannot create the database connection.")

if __name__ == '__main__':
    main()
