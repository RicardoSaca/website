from flask import Flask, render_template, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contactme')
def contact():
    return render_template("contact.html")

@app.route('/portfolio')
def portfolio():
    return render_template("portfolio.html")

if __name__ == '__main__':
    app.run(debug=True)