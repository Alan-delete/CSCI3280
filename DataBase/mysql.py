import pymysql

HOST = 'localhost'
USER = 'csci3280'
PASSWORD = 'csci3280'
DATABASE = 'project'
ATTRIBUTES = {'id': 'INT AUTO_INCREMENT PRIMARY KEY',
              'name': 'CHAR(40) NOT NULL',
              'time': 'TIME NOT NULL',
              'author': 'CHAR(40)',
              'album' : 'CHAR(40)'}

class my_Database():
    def __init__(self, host = HOST,user= USER, password= PASSWORD, database= DATABASE ) -> None:
        try:
            self.conn = pymysql.connect(
            host= host,       
            user= user,    
            passwd= password,  
            database= database
            )
        # database not initialized 
        except pymysql.err.OperationalError:
            self.conn = pymysql.connect(
            host= host,       
            user= user,    
            passwd= password,  
            )
            
            self.conn.cursor().execute("CREATE DATABASE %s"%(database))
            self.conn.select_db(database)

        #cursor = self.conn.cursor()


    def close(self):
        self.conn.close()

    def drop_table(self,  table:str = 'musics'):
        sql = "DROP TABLE IF EXISTS " + table  # 删除数据表 
        cursor = self.conn.cursor()
        cursor.execute(sql)

    # {attribute1: property1, ...}
    def create_table(self, attributes:dict, table:str = 'musics'):
        sql = "CREATE TABLE IF NOT EXISTS musics (" + ''.join(
            [ key + ' ' + attributes[key] + (',' if idx < (len(attributes) - 1) else '')
             for idx, key in enumerate(attributes.keys())]) + ")"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        self.conn.commit()

    # {attribute1: value1, ...}
    def insert(self, new_row:dict , table:str = 'musics'):
        sql = "INSERT INTO " + table + " (" \
        + ''.join([ key +  (',' if idx < (len(new_row) - 1) else ') VALUES (' ) for idx, key in enumerate(new_row.keys())]) \
        + ''.join(["%s" + (',' if idx < (len(new_row) - 1) else ')' ) for idx in range(len(new_row))]) 
        val = [new_row[key] for key in new_row]
        cursor = self.conn.cursor()
        cursor.execute(sql, val)
        self.conn.commit()  

    # implement select sql and return a dictionary
    def select(self, sql = None, table:str = 'musics')->dict:
        if not sql:
            sql = "SELECT * FROM " + table
        cursor = self.conn.cursor()
        cursor.execute(sql)   
        res = cursor.fetchall()  

        cursor.execute("DESC " + table)   
        attr_record = cursor.fetchall()

        data = [ { attr[0] :row[i] for i, attr in enumerate(attr_record) } for row in res]
        return data
    
    # search by name 
    def query_by_name(self, name:str, table:str = 'musics' ):
        sql =  "SELECT * FROM " + table + " WHERE name LIKE '%%%s%%'"%(name)
        # or 
        sql =  "SELECT * FROM " + table + " WHERE name LIKE '%{}%'".format(name)
        return self.select(sql = sql, table = table)

    # search by author 
    def query_by_author(self, author:str, table:str = 'musics' ):
        sql =  "SELECT * FROM " + table + " WHERE author LIKE '%%%s%%'"%(author)
        # or 
        sql =  "SELECT * FROM " + table + " WHERE author LIKE '%{}%'".format(author)
        return self.select(sql = sql, table = table)    


db = my_Database()

db.drop_table()
db.create_table(ATTRIBUTES)

row = {"name":"yellow", "time":":04:11", "author":"coldplay"}
db.insert(row)

data = db.query_by_author("old")
print(data)

db.close()