from flask import Flask, render_template

app = Flask(__name__)

@app.rout('/')
def home():
    return render_template(home.html)