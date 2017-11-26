import logging
import os
import stripe
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, redirect, request, send_from_directory
from config import testkey, prodkey, testsecretkey, prodsecretkey

KEY = testkey
SECRET = testsecretkey
QUANTITIES = [1, 2,]
LOGDIR = '/var/log/ruthgracewong/'
LOGFILE = 'app.log'
IPHONE_SHIPPING_COST = 10

app = Flask(__name__)
if not os.path.exists(LOGDIR):
    os.makedirs(LOGDIR)
handler = RotatingFileHandler(LOGDIR + LOGFILE, maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

def get_numbers(quantity, cost):
    numbers = {}
    numbers['quantity'] = quantity
    numbers['cost'] = cost * numbers['quantity']
    numbers['totalcents'] = 0
    numbers['totaldollars'] = numbers['cost']
    numbers['stripetotal'] = numbers['totaldollars'] * 100 + numbers['totalcents']
    return numbers

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/iphone', methods = ['GET', 'POST'])
def iphone_shipping():
    if request.method == 'GET':
        numbers = get_numbers(1, IPHONE_SHIPPING_COST)
        return render_template('iphone.html',
                               key=KEY,
                               quantities=QUANTITIES,
                               quantity=numbers['quantity'],
                               cost=numbers['cost'],
                               totalcents=numbers['totalcents'],
                               totaldollars=numbers['totaldollars'],
                               stripetotal=numbers['stripetotal'])
    if request.method == 'POST':
        numbers = get_numbers(int(request.form.get('quantity')), IPHONE_SHIPPING_COST)
        return render_template('iphone.html',
                               key=KEY,
                               quantities=QUANTITIES,
                               quantity=numbers['quantity'],
                               cost=numbers['cost'],
                               totalcents=numbers['totalcents'],
                               totaldollars=numbers['totaldollars'],
                               stripetotal=numbers['stripetotal'])

@app.route('/thankyou', methods = ['POST'])
def checkout():
    token = request.form.get('stripeToken')
    amount = request.form.get('stripetotal')
    stripe.api_key = SECRET
    charge = stripe.Charge.create(
      amount=str(amount),
      description="Shipping for iPhone toy",
      currency="usd",
      receipt_email=request.form.get('stripeEmail'),
      source=token
    )
    return render_template('thankyou.html')

@app.route('/donate', methods = ['POST'])
def donate():
    token = request.form.get('stripeToken')
    amount = request.form.get('stripetotal')
    stripe.api_key = SECRET
    charge = stripe.Charge.create(
      amount=str(amount),
      description="Donate money to Ruth",
      currency="usd",
      receipt_email=request.form.get('stripeEmail'),
      source=token
    )
    return render_template('donate.html')
