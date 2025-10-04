import pyodbc
connection_string = (r"Driver={SQL Server Native Client 11.0};"
                      r"Server=LAPTOP-AM3LGIK4\SQLEXPRESS;"
                      r"Database=favori_yemek;"
                      r"Trusted_Connection=yes;")


connection = pyodbc.connect(connection_string)
print("veri tabanına bağlandı.")