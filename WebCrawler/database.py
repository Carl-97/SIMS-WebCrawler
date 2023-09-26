import mysql.connector

class database:
    def __init__(self, db_name, db_user, db_password, db_host, db_port) :
        self.conn = mysql.connector.connect(database=db_name, user=db_user, password=db_password, host = db_host, port=db_port)
        self.cursor = self.conn.cursor()

    def get_conn(self):
        return self.conn
    def close(self):
        self.conn.close()