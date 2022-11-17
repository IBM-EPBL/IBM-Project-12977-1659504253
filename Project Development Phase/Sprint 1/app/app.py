"""
Spyder Editor

This is a temporary script file.
"""

from flask import Flask, render_template, request, redirect, session 
import re
import ibm_db


app = Flask(__name__)


app.secret_key = 'a'


# mysql = MySQL(app)

print('Connecting')
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=1bbf73c5-d84a-4bb0-85b9-ab1a4348f4a4.c3n41cmd0nqnrk39u98g.databases.appdomain.cloud;PORT=32286;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=qtj16063;PWD=bc2ajnvAWdNQEqCA",'','')
print('Connected')


#HOME--PAGE
@app.route("/home")
def home():
    return render_template("homepage.html")

@app.route("/")
def add():
    return render_template("home.html")

#LOGIN--PAGE
    
@app.route("/signin")
def signin():
    return render_template("login_new.html")
        
@app.route('/login',methods =['GET', 'POST'])
def login():
    global userid
    msg = ''
   
  
    if request.method == 'POST' :
        username = request.form['username']
        password = request.form['password']
        print(username)
        print(password)

        sql = "SELECT * FROM REGISTER WHERE email =? AND pass=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print (account)
        
        if account:
            session['loggedin'] = True
            session['id'] = account['EMAIL']
            userid =  account['EMAIL']
            session['username'] = account['EMAIL']
        
            return redirect('/home')
        else:
            msg = 'Incorrect username / password !'
    # return render_template('login.html', msg = msg)
    return render_template('login_new.html', msg = msg)


#log-out

@app.route('/logout')

def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return render_template('home.html')

             

if __name__ == "__main__":
    # app.run(debug=True)
    app.run()