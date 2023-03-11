import pymysql

HOST = 'localhost'
USER = 'csci3280'
PASSWORD = 'csci3280'
DATABASE = 'project'



try:
    conn = pymysql.connect(
    host= HOST,       
    user= USER,    
    passwd= PASSWORD,  
    database= DATABASE
    )
# database not initialized 
except pymysql.err.OperationalError:
    conn = pymysql.connect(
    host=HOST,      
    user=USER,   
    passwd=PASSWORD  
    )
    
    conn.cursor().execute("CREATE DATABASE %s"%(DATABASE))
    conn.select_db(DATABASE)

cursor = conn.cursor()

sql = "DROP TABLE IF EXISTS musics"  # 删除数据表 sites
 
cursor.execute(sql)


sql = """CREATE TABLE musics (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name CHAR(40) NOT NULL,
        time TIME NOT NULL,
        author CHAR(40),
        album CHAR(40)
        )"""

cursor.execute(sql)


sql = "INSERT INTO musics (name, time, author, album) VALUES (%s, %s, %s ,%s)"
val = ("yellow", ":04:11", "coldplay","")
cursor.execute(sql,val)
conn.commit()

cursor.execute("SELECT * FROM musics")

data = cursor.fetchall()
print(data)

conn.close()


def insert(name, time, author, album):
    sql = "INSERT INTO sites (name, time, author, album) VALUES (%s, %s, %s ,%s)"
    val = (name, time, author,album)
