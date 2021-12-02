from flask import Flask, render_template, request, redirect
import pyodbc
app = Flask(__name__, template_folder='./pages')

server = 'funtimesserver.database.windows.net'
database = 'CCDatabase'
DBusername = 'admin2'
DBpassword = '{Password2}'
DBdriver = '{ODBC Driver 13 for SQL Server}'

conn = pyodbc.connect('DRIVER='+DBdriver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+DBusername+';PWD='+ DBpassword)
cursor = conn.cursor()
cursor.execute("SELECT * FROM [dbo].[viewColNames]")
logged_in = False
column_names = cursor.fetchall()

@app.route("/", methods=['GET', 'POST'])
def landing_page():
    global logged_in
    logged_in = False
    response = ""
    if request.method == 'POST':
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


@app.route('/upload')
def upload():
    if logged_in:
        return render_template('upload.html', logged_in=logged_in)
    else:
        return redirect('/')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    global logged_in
    logged_in = False
    response = ""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('pw')
        email = request.form.get('email')
        if password is not "" and username is not "" and email is not "":
            cursor.execute("SELECT * FROM [dbo].[users] where username = '" + username + "'")
            userExists = cursor.fetchone()
            if userExists == None:
                cursor.execute("INSERT INTO[dbo].[users]([username], [pswd], [email]) VALUES( '" + username + "','" + password + "','" + email + "')")
                conn.commit()
                logged_in = True
                return redirect('/home')
            else:
                response = "Username already in use"
        else:
            response = "Please enter the required information"
    return render_template('signup.html', logged_in=logged_in, response=response)

if __name__ == "__main__":
    app.run()