from flask import Flask, render_template, request, redirect, url_for
import pyodbc
import pandas as pd
import csv
app = Flask(__name__, template_folder='./pages')

server = 'funtimesserver.database.windows.net'
database = 'CCDatabase'
DBusername = 'admin2'
DBpassword = '{Password2}'
DBdriver = '{ODBC Driver 17 for SQL Server}'
connString = 'DRIVER='+DBdriver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+DBusername+';PWD='+ DBpassword
conn = pyodbc.connect(connString)
cursortemp = conn.cursor()
cursortemp.execute("SELECT * FROM [dbo].[viewColNames]")
logged_in = False
column_names = cursortemp.fetchall()
conn.close()

@app.route("/", methods=['GET', 'POST'])
def landing_page():
    global logged_in
    logged_in = False
    response = ""
    if request.method == 'POST':
        with pyodbc.connect(connString) as conn:
            cursor = conn.cursor()
            username = request.form.get('username')
            password = request.form.get('pw')
            if password is not "" and username is not "":
                cursor.execute("SELECT * FROM [dbo].[users] where username = '" + username +"'")
                userExists = cursor.fetchone()
                if userExists != None and userExists[2] == password:

                    logged_in = True
                    return redirect('/home')
                else:
                    response = "Username and/or password are incorrect"
            else:
                response = "Please enter your username and password"
    return render_template('login.html', response=response)

# @app.route("/login")
# def login():
#     return render_template('login.html')

@app.route('/home')
def home():
    if logged_in:
        with pyodbc.connect(connString) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM [dbo].[joinedTables] WHERE HSHD_NUM = 10 ORDER BY Hshd_num, Basket_num, PURCHASE, Product_num, Department, Commodity")
            rows = cursor.fetchall()
        return render_template('index.html', column_names=column_names, rows=rows, logged_in=logged_in)

    else:
        return redirect('/')


@app.route('/data', methods=['GET', 'POST'])
def data():
    rows = None
    if logged_in:
        if request.method == 'POST':
            with pyodbc.connect(connString) as conn:
                cursor = conn.cursor()
                household_num = request.form.get('householdnum')
                if household_num != "":
                    cursor.execute("SELECT * FROM [dbo].[joinedTables] WHERE HSHD_NUM = " + household_num + " ORDER BY Hshd_num, Basket_num, PURCHASE, Product_num, Department, Commodity")
                    rows = cursor.fetchall()
        return render_template('data.html', logged_in=logged_in, column_names=column_names, rows=rows)
    else:
        return redirect('/')


@app.route('/engagement-over-time')
def engagement_over_time():
    if logged_in:
        return render_template('engagement-over-time.html', column_names=column_names, logged_in=logged_in)
    else:
        return redirect('/')


@app.route('/demographic-factors')
def demographic_factors():
    global logged_in
    if logged_in:
        return render_template('demographic-factors.html', logged_in=logged_in)
    else:
        return redirect('/')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if logged_in:
        if request.method == 'POST':
            try:
                with pyodbc.connect(connString) as conn:
                    cursor = conn.cursor()
                    if request.files['households']:
                        print('households upload')
                        households_filestream = request.files['households'].stream
                        households_df = pd.read_csv(households_filestream, names=["HSHD_NUM", "L", "AGE_RANGE", "MARITAL", "INCOME_RANGE", "HOMEOWNER", "HSHD_COMPOSITION", "HH_SIZE", "CHILDREN"], skiprows=1)
                        households_df = households_df.astype({"CHILDREN": str})
                        for row in households_df.itertuples():
                            cursor.execute('''INSERT INTO [dbo].[400_households] (HSHD_NUM, L, AGE_RANGE, MARITAL, INCOME_RANGE, HOMEOWNER, HSHD_COMPOSITION, HH_SIZE, CHILDREN) VALUES (?,?,?,?,?,?,?,?,?)''',
                                           row.HSHD_NUM, row.L, row.AGE_RANGE, row.MARITAL, row.INCOME_RANGE, row.HOMEOWNER, row.HSHD_COMPOSITION, row.HH_SIZE, row.CHILDREN)

                    if request.files['products']:
                        print('products upload')
                        products_filestream = request.files['products'].stream
                        products_df = pd.read_csv(products_filestream, names=["PRODUCT_NUM", "DEPARTMENT", "COMMODITY", "BRAND_TY", "NATURAL_ORGANIC_FLAG"], skiprows=1)
                        for row in products_df.itertuples():
                            cursor.execute('''INSERT INTO [dbo].[400_products] (PRODUCT_NUM, DEPARTMENT, COMMODITY, BRAND_TY, NATURAL_ORGANIC_FLAG) VALUES (?,?,?,?,?)''',
                                           row.PRODUCT_NUM, row.DEPARTMENT, row.COMMODITY, row.BRAND_TY, row.NATURAL_ORGANIC_FLAG)

                    if request.files['transactions']:
                        print('transactions upload')
                        transactions_filestream = request.files['transactions'].stream
                        transactions_df = pd.read_csv(transactions_filestream,names=["BASKET_NUM", "HSHD_NUM", "PURCHASE_", "PRODUCT_NUM", "SPEND", "UNITS", "STORE_R", "WEEK_NUM", "YEAR"], skiprows=1)
                        for row in transactions_df.itertuples():
                            cursor.execute('''INSERT INTO [dbo].[400_transactions] (BASKET_NUM, HSHD_NUM, PURCHASE, PRODUCT_NUM, SPEND, UNITS, STORE_R, WEEK_NUM, YEAR) VALUES (?,?,?,?,?,?,?,?,?)''',
                                           row.BASKET_NUM, row.HSHD_NUM, row.PURCHASE_, row.PRODUCT_NUM, row.SPEND, row.UNITS, row.STORE_R, row.WEEK_NUM, row.YEAR)
                    conn.commit()
                    return redirect("/data")
            except Exception:
                return redirect("/error")
        return render_template('upload.html', logged_in=logged_in)
    else:
        return redirect('/')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    global logged_in
    logged_in = False
    response = ""
    if request.method == 'POST':
        with pyodbc.connect(connString) as conn:
            cursor = conn.cursor()
            username = request.form.get('username')
            password = request.form.get('pw')
            email = request.form.get('email')
            if password is not "" and username is not "" and email is not "":
                cursor.execute("SELECT * FROM [dbo].[users] where username = '" + username + "'")
                userExists = cursor.fetchone()
                if userExists == None:
                    cursor.execute("INSERT INTO [dbo].[users]([username], [pswd], [email]) VALUES( '" + username + "','" + password + "','" + email + "')")
                    conn.commit()
                    logged_in = True
                    return redirect('/home')
                else:
                    response = "Username already in use"
            else:
                response = "Please enter the required information"
    return render_template('signup.html', logged_in=logged_in, response=response)

@app.route('/error')
def errorPage():
    return render_template('error.html', logged_in=logged_in)
if __name__ == "__main__":
    app.run()