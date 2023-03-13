import pymysql

HOST = 'localhost'
USER = 'csci3280'
PASSWORD = 'csci3280'
DATABASE = 'project'
ATTRIBUTES = {'id': 'INT AUTO_INCREMENT PRIMARY KEY',
              'name': 'CHAR(40) NOT NULL',
              'time': 'TIME NOT NULL',
              'author': 'CHAR(40)',
              'album' : 'CHAR(40)',
              'location' : 'CHAR(40)'}

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

    def drop_table(self,  table:str = 'music'):
        sql = "DROP TABLE IF EXISTS " + table   
        cursor = self.conn.cursor()
        cursor.execute(sql)

    # {attribute1: property1, ...}
    def create_table(self, attributes:dict, table:str = 'music'):
        sql = "CREATE TABLE IF NOT EXISTS music (" + ''.join(
            [ key + ' ' + attributes[key] + (',' if idx < (len(attributes) - 1) else '')
             for idx, key in enumerate(attributes.keys())]) + ")"
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            self.conn.commit()
        except:
            print("Execution error")
            self.conn.rollback()

    # {attribute1: value1, ...}
    def insert(self, new_row:dict , table:str = 'music'):
        sql = "INSERT INTO " + table + " (" \
        + ''.join([ key +  (',' if idx < (len(new_row) - 1) else ') VALUES (' ) for idx, key in enumerate(new_row.keys())]) \
        + ''.join(["%s" + (',' if idx < (len(new_row) - 1) else ')' ) for idx in range(len(new_row))]) 
        val = [new_row[key] for key in new_row]
        cursor = self.conn.cursor()
        try:
            cursor.execute(sql, val)
            self.conn.commit()
        except:
            print("Execution error")
            self.conn.rollback()

    # insert if the row did not exist, otherwise update it
    def insert_or_update(self, new_row:dict , table:str = 'music'):
        sql = "INSERT INTO " + table + " (" \
        + ''.join([ key +  (',' if idx < (len(new_row) - 1) else ') VALUES (' ) for idx, key in enumerate(new_row.keys())]) \
        + ''.join([ "'{}'".format(new_row[key]) + (',' if idx < (len(new_row) - 1) else ')' ) for idx, key in enumerate(new_row.keys())]) \
        + " ON DUPLICATE KEY UPDATE "  \
        + ''.join([ "{} = '{}'".format(key, new_row[key]) + (',' if idx < (len(new_row) - 1) else '' ) for idx, key in enumerate(new_row.keys())])  

        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            self.conn.commit()
        except:
            print("Execution error")
            self.conn.rollback()


    # implement select sql and return a dictionary
    def select(self, sql = None, table:str = 'music')->dict:
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
    def query_by_name(self, name:str, table:str = 'music' ):
        sql =  "SELECT * FROM " + table + " WHERE name LIKE '%{}%'".format(name)
        return self.select(sql = sql, table = table)

    # search by author 
    def query_by_author(self, author:str, table:str = 'music' ):
        sql =  "SELECT * FROM " + table + " WHERE author LIKE '%{}%'".format(author)
        return self.select(sql = sql, table = table)    
    
    # search by name, author as well as album
    def query_by_all(self, query :str, table:str = 'music' ):
        sql =  "SELECT * FROM " + table + " WHERE name LIKE '%{}%'".format(query)\
        + " OR author LIKE '%{}%'".format(query) + " OR album LIKE '%{}%'".format(query)
        return self.select(sql = sql, table = table)    

    # simple delete operation, the default operation is to empty the table 
    def delete(self, id = None, sql = None, table: str = 'music'):
        # both sql and id is None, use default deletion
        if not sql and not id:
            sql =  "DELETE FROM " + table
        elif not sql:
            sql = "DELETE FROM " + table + " WHERE id  = {}".format(id) 

        cursor = self.conn.cursor()
        try:
            cursor.execute(sql)
            self.conn.commit()
            # later delete the wav file ...
        except:
            print("Execution error")
            self.conn.rollback()
        

# All API's default taget is "music" table, so current we don't need to set this function parameter

# TEST API
db = my_Database()

# Initialize an empty table
db.drop_table()
db.create_table(ATTRIBUTES) # same as db.create_table(ATTRIBUTES, "music")

# Insert a row
row = {"name":"yellow", "time":":04:11", "author":"coldplay"}
db.insert(row)

# search the song containing "old"
data = db.query_by_all("old")
print(data)

# Insert or update a row
new_row = { "id":2 , "name":"red", "time":":04:11", "author":"coldplay"}
db.insert_or_update(new_row)
data = db.query_by_all("")
print(data)

# Delete the row with id = 1
db.delete(1)
data = db.query_by_all("")
print(data)

db.close()