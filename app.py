from flask import Flask, render_template, url_for, request, flash
from flask.helpers import get_flashed_messages
from flask_fontawesome import FontAwesome
from forms import ContactForm
from flask_mail import Message, Mail
import pandas as pd

app = Flask(__name__)

app.secret_key = 'Ilov3GreenPastur$s!'

mail_settings ={
    "MAIL_SERVER" : "smtp.gmail.com",
    "MAIL_PORT" : 465,
    "MAIL_USERNAME" : 'ricardosaca98@gmail.com',
    "MAIL_PASSWORD" : '', #Figure out safety for password!!
    "MAIL_USE_TLS" : False,
    "MAIL_USE_SSL" : True,
}
app.config.update(mail_settings)
mail = Mail(app)

fa = FontAwesome(app)

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
            print('False')
            flash('All fields are required')
            return render_template('contact.html', form=form)
        else:
            print('Hello!')
            msg = Message(form.subject.data, sender='ricardosaca98@gmail.com', recipients=['ricardosaca@gmail.com'])
            msg.body = """
            %s has contacted you. 
            You can reply to this email address <%s>
            They said:

            %s

            """ % (form.name.data, form.email.data, form.message.data)
            mail.send(msg)
            return render_template('contact.html', success=True)

    elif request.method == 'GET':
        print('gets')
        return  render_template('contact.html', form=form)

@app.route('/portfolio')
def portfolio():
    return render_template("portfolio.html")

if __name__ == "__main__":
    app.run(debug=True)