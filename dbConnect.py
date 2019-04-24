import pyodbc db

class dbConnect:

    def __init__  (self, sql, path):
        self.sql = sql
        with open(path,"r") as file:
            self.connString = file.read()

    def getData (self):
        conn = pyodbc.connect(self.connString)

        """
                              'Driver={SQL Server};'
                              'Server=server_name;'
                              'Database=db_name;'
                              'Trusted_Connection=yes;'
        """
        cursor = conn.cursor()
        result = [row for row in cursor.execute(self.url)]
        conn.close()
        return result


