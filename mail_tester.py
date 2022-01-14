from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)
mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'srmates123@gmail.com'
app.config['MAIL_PASSWORD'] = 'xxyyzz123'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

@app.route("/")
def index():
   msg = Message('Hello', sender = 'srmates123@gmail.com', recipients = ['f20180886@pilani.bits-pilani.ac.in'])
   msg.body = "Lakshit pp smol"
   mail.send(msg)
   return "Sent"

if __name__ == '__main__':
   app.run(debug = True)