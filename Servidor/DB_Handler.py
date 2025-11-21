from DB_Connector import connect_to_db
from DB_Table_Creator import create_tables
from DB_Table_Checker import *
from DB_Table_Editor import *

conn = connect_to_db()
create_tables(conn)

connect_editor(conn)
connect_checker(conn)

def create_account(username, password):
    return