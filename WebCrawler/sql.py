import mysql.connector
class Sql:
    def __init__(self, Db_connection):
        self.connect = Db_connection.get_con()
        
    #**
    #* prepares and execute sql quaries
    #* @return $stmt 
    #/
    def execute(self, query, params=None):		
        try:
            cursor = self.connect.cursor(prepared=True)
			#stmt = self.connect.prepare(command)
            if params: 
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            self.connect.commit()
            return result
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.connect.rollback()
            return None
    def close_cursor(self):
        self.cursor.close()
    #def insertData(self, table, data):
        #quary = f'INSERT INTO {table} ({',' join(columns)}) VALUES ({''})'