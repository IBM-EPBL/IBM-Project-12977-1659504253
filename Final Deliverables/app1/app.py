from flask import Flask, render_template, request, redirect, session 
# from flask_mysqldb import MySQL
# import MySQLdb.cursors
import re
import ibm_db
import datetime
import math

app = Flask(__name__)


app.secret_key = 'a'

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



#SIGN--UP--OR--REGISTER


@app.route("/signup")
def signup():
    return render_template("login_new.html")



@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' :
        username = request.form['username']
        email = username
        password = request.form['password']

        # cursor = mysql.connection.cursor()
        # cursor.execute('SELECT * FROM register WHERE username = % s', (username, ))
        # account = cursor.fetchone()
        # print(account)

        sql = "SELECT * FROM REGISTER WHERE email =?"
        print(username)
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        # print(account)

        if account:
            msg = 'Account already exists !'
            print(msg)
            return render_template('login_new.html', msg = msg)

        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
            print(msg)
            return render_template('login_new.html', msg = msg)

        else:

            sql = "insert into register values (?, ?)"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,username)
            ibm_db.bind_param(stmt,2,password)
            ibm_db.execute(stmt)
            # print(res)
            msg = 'You have successfully registered !'
            print(msg)
            return render_template('login_new.html', msg = msg)
        
        
 
        
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



       





#ADDING----DATA


@app.route("/add")
def adding():
    return render_template('add.html')


@app.route('/addexpense',methods=['GET', 'POST'])
def addexpense():
    
    date = request.form['date'] + ''
    expensename = request.form['expensename'] + ''
    amount = request.form['amount'] + ''
    paymode = request.form['paymode'] + ''
    category = request.form['category'] + ''
    
    print(date + " " + expensename + " " + amount + " " + paymode + " " + category)

    today = str(datetime.datetime.today())
    date = date.split('T')[0]
    today = today[:11]
    sql = "select limit from limits where email = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,session['id'])
    ibm_db.execute(stmt)
    lim = ibm_db.fetch_tuple(stmt)
    if not lim:
        lim = math.inf
    else:
        lim = int(lim[0])

    if today <= date:
        msg = "Date can't be in future"
        return render_template('add.html', msg = msg)
    else:
        month = today[:7]
        if date[:7] == month:
            sql = "select * from expenses where email = ? and date like '" + month + "%'"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,session['id'])
            ibm_db.execute(stmt)
            expense = ibm_db.fetch_tuple(stmt)
            month_total = 0
            while expense:
                month_total += int(expense[4])
                expense = ibm_db.fetch_tuple(stmt)

            if lim >= month_total + int(amount):
                sql = "insert into expenses (email, date, expensename, amount, paymode, category) values (?, ?, ?, ?, ?, ?)"
                stmt = ibm_db.prepare(conn, sql)
                ibm_db.bind_param(stmt,1,session['id'])
                ibm_db.bind_param(stmt,2, date)
                ibm_db.bind_param(stmt,3, expensename)
                ibm_db.bind_param(stmt,4, amount)
                ibm_db.bind_param(stmt,5, paymode)
                ibm_db.bind_param(stmt,6, category)
                ibm_db.execute(stmt)
                return redirect("/display")

            else:
                msg = "Monthly limit exceeded"
                return render_template('add.html', msg="Can't add expense as monthly limit exceeded")

        else:
            sql = "insert into expenses (email, date, expensename, amount, paymode, category) values (?, ?, ?, ?, ?, ?)"
            stmt = ibm_db.prepare(conn, sql)
            ibm_db.bind_param(stmt,1,session['id'])
            ibm_db.bind_param(stmt,2, date)
            ibm_db.bind_param(stmt,3, expensename)
            ibm_db.bind_param(stmt,4, amount)
            ibm_db.bind_param(stmt,5, paymode)
            ibm_db.bind_param(stmt,6, category)
            ibm_db.execute(stmt)
            return redirect("/display")




#DISPLAY---graph 

@app.route("/display")
def display():
    print(session['id'])

    total = 0
    t_food = 0
    t_entertainment = 0
    t_business = 0
    t_rent = 0
    t_EMI = 0
    t_other = 0

    sql = "SELECT * FROM expenses WHERE email = ? order by expenses.date desc"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,session['id'])
    ibm_db.execute(stmt)
    expense_list = []
    expense = ibm_db.fetch_tuple(stmt)

    if expense:
        expense = list(expense)
        expense[2] = expense[2].replace('T', '  ')
        expense_list.append(expense)

    while expense != False:
        expense = ibm_db.fetch_tuple(stmt)
        if expense:
            expense = list(expense)
            expense[2] = expense[2].replace('T', '  ')
            expense_list.append(expense)

    for x in expense_list:
        total += int(x[4])
        if x[6] == "food":
            t_food += int(x[4])

        elif x[6] == "entertainment":
            t_entertainment += int(x[4])

        elif x[6] == "business":
            t_business += int(x[4])

        elif x[6] == "rent":
            t_rent += int(x[4])

        elif x[6] == "EMI":
            t_EMI += int(x[4])

        elif x[6] == "other":
            t_other += int(x[4])


    
    
    return render_template('display.html' ,texpense = expense_list, expense=expense_list,  total=total,
                            t_food=t_food, t_entertainment=t_entertainment,
                            t_business=t_business,  t_rent=t_rent,
                            t_EMI=t_EMI,  t_other=t_other)



# delete---the--data

@app.route('/delete/<string:id>', methods = ['POST', 'GET' ])
def delete(id):
    #  cursor = mysql.connection.cursor()
    #  cursor.execute('DELETE FROM expenses WHERE  id = {0}'.format(id))
    #  mysql.connection.commit()
    #  print('deleted successfully') 
    
    sql = "delete from expenses where id = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,id)
    ibm_db.execute(stmt)

    return redirect("/display")
 
    
# #UPDATE---DATA

# @app.route('/edit/<id>', methods = ['POST', 'GET' ])
# def edit(id):
    # cursor = mysql.connection.cursor()
    # cursor.execute('SELECT * FROM expenses WHERE  id = %s', (id,))
    # row = cursor.fetchall()
    
    # print(row[0])
    # return render_template('edit.html', expenses = row[0])




# @app.route('/update/<id>', methods = ['POST'])
# def update(id):
#   if request.method == 'POST' :
   
#       date = request.form['date']
#       expensename = request.form['expensename']
#       amount = request.form['amount']
#       paymode = request.form['paymode']
#       category = request.form['category']
    
#       cursor = mysql.connection.cursor()
       
#       cursor.execute("UPDATE `expenses` SET `date` = % s , `expensename` = % s , `amount` = % s, `paymode` = % s, `category` = % s WHERE `expenses`.`id` = % s ",(date, expensename, amount, str(paymode), str(category),id))
#       mysql.connection.commit()
#       print('successfully updated')
#       return redirect("/display")



#  #limit
@app.route("/limit" )
def limit():
    sql = "select limit from limits where email = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,session['id'])
    ibm_db.execute(stmt)
    lim = ibm_db.fetch_tuple(stmt)
    print(lim)
    msg = ""
    if lim:
        msg = "Currently your MONTHLY limit is ₹ " + lim[0]

    else:
        msg = "Currently no monthly limit is set"

    return render_template('limit.html', y=msg)

@app.route("/limitnum" , methods = ['POST', 'GET' ])
def limitnum():
    sql = "select limit from limits where email = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,session['id'])
    ibm_db.execute(stmt)
    msg = "Currently your MONTHLY limit is ₹ "
    lim = ibm_db.fetch_tuple(stmt)
    if not lim:
        number = request.form['number'] + ''
        sql = "insert into limits values (?, ?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['id'])
        ibm_db.bind_param(stmt,2,number)
        ibm_db.execute(stmt)
        msg += number

    if limit:
        number = request.form['number'] + ''
        sql = "update limits set limit = ? where email = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,number)
        ibm_db.bind_param(stmt,2,session['id'])
        ibm_db.execute(stmt)
        msg += number
    return redirect('/limit')

# #REPORT

@app.route("/today")
def today():
    ttotal = 0
    import datetime
    x = datetime.datetime.now()
    y = str(x).split(' ')[0]

    sql = "SELECT * FROM expenses  WHERE email = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,session['id'])
    ibm_db.execute(stmt)
    expense_list = []
    texpense_list = []
    expense = ibm_db.fetch_tuple(stmt)
    if expense:
        print(expense[2])
        date = expense[2].split('T')[0]
        ttotal += int(expense[4])
        texpense_list.append(expense)
        print(date)
        print(y)
        if date == y:
            expense_list.append(expense)
            print(expense)

        while expense != False:
            expense = ibm_db.fetch_tuple(stmt)

            if expense != False:
                ttotal += int(expense[4])
                texpense_list.append(expense)
                date = expense[2].split('T')[0]
                if date == y:
                    expense_list.append(expense)
                    print(expense)
    total = 0
    t_food = 0
    t_entertainment = 0
    t_business = 0
    t_rent = 0
    t_EMI = 0
    t_other = 0

    for x in expense_list:
        total += int(x[4])
        if x[6] == "food":
            t_food += int(x[4])

        elif x[6] == "entertainment":
            t_entertainment += int(x[4])

        elif x[6] == "business":
            t_business += int(x[4])

        elif x[6] == "rent":
            t_rent += int(x[4])

        elif x[6] == "EMI":
            t_EMI += int(x[4])

        elif x[6] == "other":
            t_other += int(x[4])

    print(total)

    print(t_food)
    print(t_entertainment)
    print(t_business)
    print(t_rent)
    print(t_EMI)
    print(t_other)

    return render_template("today.html", texpense = texpense_list, expense=expense,  total=total,
                            t_food=t_food, t_entertainment=t_entertainment,
                            t_business=t_business,  t_rent=t_rent,
                            t_EMI=t_EMI,  t_other=t_other)


@app.route("/month")
def month():
    ttotal = 0
    import datetime
    x = datetime.datetime.now()
    month = str(x).split()[0].split('-')
    y = month[0] + '-' + month[1]

    sql = "SELECT * FROM expenses  WHERE email = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,session['id'])
    ibm_db.execute(stmt)
    expense_list = []
    texpense_list = []
    expense = ibm_db.fetch_tuple(stmt)
    if expense:
        date = expense[2].split('T')[0].split('-')
        date = date[0] + '-' + date[1]
        ttotal += int(expense[4])
        texpense_list.append(expense)
        print(date)
        print(y)
        if date == y:
            expense_list.append(expense)
            print(expense)

        while expense != False:
            expense = ibm_db.fetch_tuple(stmt)

            if expense != False:
                ttotal += int(expense[4])
                texpense_list.append(expense)
                date = expense[2].split('T')[0].split('-')
                date = date[0] + '-' + date[1]
                if date == y:
                    expense_list.append(expense)
                    print(expense)
    total = 0
    t_food = 0
    t_entertainment = 0
    t_business = 0
    t_rent = 0
    t_EMI = 0
    t_other = 0

    for x in expense_list:
        total += int(x[4])
        if x[6] == "food":
            t_food += int(x[4])

        elif x[6] == "entertainment":
            t_entertainment += int(x[4])

        elif x[6] == "business":
            t_business += int(x[4])

        elif x[6] == "rent":
            t_rent += int(x[4])

        elif x[6] == "EMI":
            t_EMI += int(x[4])

        elif x[6] == "other":
            t_other += int(x[4])

    print(total)

    print(t_food)
    print(t_entertainment)
    print(t_business)
    print(t_rent)
    print(t_EMI)
    print(t_other)

    return render_template("month.html", texpense = texpense_list, expense=expense,  total=total,
                            t_food=t_food, t_entertainment=t_entertainment,
                            t_business=t_business,  t_rent=t_rent,
                            t_EMI=t_EMI,  t_other=t_other)

@app.route("/year")
def year():
    ttotal = 0
    import datetime
    x = datetime.datetime.now()
    month = str(x).split()[0].split('-')
    y = month[0]

    sql = "SELECT * FROM expenses  WHERE email = ?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,session['id'])
    ibm_db.execute(stmt)
    expense_list = []
    texpense_list = []
    expense = ibm_db.fetch_tuple(stmt)
    if expense:
        date = expense[2].split('T')[0].split('-')
        date = date[0]
        ttotal += int(expense[4])
        texpense_list.append(expense)
        print(date)
        print(y)
        if date == y:
            expense_list.append(expense)
            print(expense)

        while expense != False:
            expense = ibm_db.fetch_tuple(stmt)

            if expense != False:
                ttotal += int(expense[4])
                texpense_list.append(expense)
                date = expense[2].split('T')[0].split('-')
                date = date[0]
                if date == y:
                    expense_list.append(expense)
                    print(expense)
    total = 0
    t_food = 0
    t_entertainment = 0
    t_business = 0
    t_rent = 0
    t_EMI = 0
    t_other = 0

    for x in expense_list:
        total += int(x[4])
        if x[6] == "food":
            t_food += int(x[4])

        elif x[6] == "entertainment":
            t_entertainment += int(x[4])

        elif x[6] == "business":
            t_business += int(x[4])

        elif x[6] == "rent":
            t_rent += int(x[4])

        elif x[6] == "EMI":
            t_EMI += int(x[4])

        elif x[6] == "other":
            t_other += int(x[4])

    print(total)

    print(t_food)
    print(t_entertainment)
    print(t_business)
    print(t_rent)
    print(t_EMI)
    print(t_other)

    return render_template("year.html", texpense = texpense_list, expense=expense,  total=total,
                            t_food=t_food, t_entertainment=t_entertainment,
                            t_business=t_business,  t_rent=t_rent,
                            t_EMI=t_EMI,  t_other=t_other)
#       
# #log-out

@app.route('/logout')

def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    msg = 'Successfully logged out'
    return render_template('home.html', msg = msg)

if __name__ == "__main__":
    app.run(host="0.0.0.0",debug=True)
    # app.run()