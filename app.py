import flask
import os
from flask import Flask, render_template

app = Flask(__name__, template_folder='./pages')

@app.route("/")
def landing_page():
    return render_template('login.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('index.html')

@app.route('/data')
def data():
    return render_template('data.html')

@app.route('/engagement-over-time')
def engagement_over_time():
    return render_template('engagement-over-time.html')

@app.route('/demographic-factors')
def demographic_factors():
    return render_template('demographic-factors.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

if __name__ == "__main__":
    app.run()