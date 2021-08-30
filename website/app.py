from flask import Flask, render_template, url_for, request, flash
from flask.helpers import get_flashed_messages
from forms import ContactForm
from flask_mail import Message, Mail
from configparser import ConfigParser
import os

app = Flask(__name__)

#setup config parser to read sensitive information
config = ConfigParser()
config.read('config/keys_config.cfg', encoding=None)

#Gather sensitive information
SECRET_KEY = os.environ.get('secret_key')
MAIL_USER = os.environ.get('EMAIL_USERNAME')
PASSWORD = os.environ.get('EMAIL_PASSWORD')

app.secret_key = SECRET_KEY

mail_settings ={
    "MAIL_SERVER" : "smtp.gmail.com",
    "MAIL_PORT" : 465,
    "MAIL_USERNAME" : MAIL_USER,
    "MAIL_PASSWORD" : PASSWORD,
    "MAIL_USE_TLS" : False,
    "MAIL_USE_SSL" : True,
}
app.config.update(mail_settings)
mail = Mail(app)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contactme', methods=['GET','POST'])
def contact():
    form = ContactForm()

    if request.method == 'POST':
        if form.validate() == False:
            flash('All fields are required')
            return render_template('contact.html', form=form)
        else:
            try:
                msg = Message(f'Message from {form.name.data}', sender='ricardosaca98@gmail.com', recipients=['ricardosaca@gmail.com'])
                msg.body = """
                %s has contacted you.
                You can reply to this email address <%s>
                They said:

                %s

                """ % (form.name.data, form.email.data, form.message.data)
                mail.send(msg)
                print("success! email sent")
                return render_template('contact.html', success=True)
            except:
                import sys
                e = sys.exc_info()[0]
                print("error! email failed to send")
                print(e)
                return render_template('error.html')

    elif request.method == 'GET':
        return  render_template('contact.html', form=form)

@app.route('/portfolio')
def portfolio():
    return render_template("portfolio.html")

@app.route('/bookshelf')
def bookshelf():
    return render_template("bookshelf.html")

@app.route('/comingsoon')
def comingsoon():
    return render_template("comingsoon.html")

@app.route('/error')
def error():
    return render_template("error.html")

if __name__ == "__main__":
    app.run()