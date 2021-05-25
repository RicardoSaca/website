from flask import Flask, render_template, url_for, request, flash
from flask_fontawesome import FontAwesome
from forms import ContactForm
import pandas as pd

app = Flask(__name__)
app.secret_key = 'secretKey'
fa = FontAwesome(app)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

# @app.route('/contactme', methods=["GET","POST"])
# def contact():
#     form = ContactForm()
#     if request.method == 'POST':
#         name = request.form["name"]
#         email = request.form["email"]
#         subject = request.form["subject"]
#         message = request.form["message"]
#         res = pd.DataFrame({'name':name, 'email':email, 'subject':subject, 'message':message}, index=[0])
#         res.to_csv('./contactusMessage.csv')
#         print("The data are saved!")
#         return render_template('contact.html', form=form)
#     else:
#         return render_template("contact.html", form=form)

@app.route('/contactme', methods=['GET','POST'])
def contact():
    form = ContactForm()

    if request.method == 'POST':
        return 'Form posted.'
    elif request.method == 'GET':
        return  render_template('contact.html', form=form)

@app.route('/portfolio')
def portfolio():
    return render_template("portfolio.html")

if __name__ == "__main__":
    app.run(debug=True)