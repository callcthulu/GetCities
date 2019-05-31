import pyodbc as db


class DBConnect:

    def __init__  (self, sql, path):
        self.sql = sql
        with open(path,"r") as file:
            self.connString = file.read()

    def getData (self):
        conn = db.connect(self.connString)

        """
                              'Driver={SQL Server};'
                              'Server=server_name;'
                              'Database=db_name;'
                              'Trusted_Connection=yes;'
        """
        cursor = conn.cursor()
        result = [row for row in cursor.execute(self.sql)]
        conn.close()
        return result


