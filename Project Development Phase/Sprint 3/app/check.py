import ibm_db

print("Hello")
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=qtj16063;PWD=bc2ajnvAWdNQEqCA",'','')
print("connected")

sql = "SELECT * FROM expenses WHERE email = ? order by expenses.date desc"
stmt = ibm_db.prepare(conn, sql)
ibm_db.bind_param(stmt,1,'admin@budget')
ibm_db.execute(stmt)
expense = ibm_db.fetch_tuple(stmt)
print(expense)