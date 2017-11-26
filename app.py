import logging
import os
import stripe
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, redirect, request, send_from_directory
from config import testkey, prodkey, testsecretkey, prodsecretkey

KEY = prodkey
SECRET = prodsecretkey
QUANTITIES = [1, 2,]
LOGDIR = '/var/log/ruthgracewong/'
LOGFILE = 'app.log'

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
    numbers['taxtotalcents'] = (85 * numbers['cost']) / 10
    numbers['taxcents'] = numbers['taxtotalcents'] % 100
    numbers['taxdollars'] = numbers['taxtotalcents'] / 100
    numbers['totalcents'] = numbers['taxcents']
    numbers['totaldollars'] = numbers['taxdollars'] + numbers['cost']
    numbers['stripetotal'] = numbers['totaldollars'] * 100 + numbers['totalcents']
    return numbers

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ten', methods = ['GET', 'POST'])
def ten_dollars():
    if request.method == 'GET':
        numbers = get_numbers(1, 10)
        return render_template('ten.html',
                               key=KEY,
                               quantities=QUANTITIES,
                               quantity=numbers['quantity'],
                               cost=numbers['cost'],
                               taxcents=numbers['taxcents'],
                               taxdollars=numbers['taxdollars'],
                               totalcents=numbers['totalcents'],
                               totaldollars=numbers['totaldollars'],
                               stripetotal=numbers['stripetotal'])
    if request.method == 'POST':
        numbers = get_numbers(int(request.form.get('quantity')), 10)
        return render_template('ten.html',
                               key=KEY,
                               quantities=QUANTITIES,
                               quantity=numbers['quantity'],
                               cost=numbers['cost'],
                               taxcents=numbers['taxcents'],
                               taxdollars=numbers['taxdollars'],
                               totalcents=numbers['totalcents'],
                               totaldollars=numbers['totaldollars'],
                               stripetotal=numbers['stripetotal'])

@app.route('/checkout', methods = ['POST'])
def checkout():
    token = request.form.get('stripeToken')
    amount = request.form.get('stripetotal')
    stripe.api_key = SECRET
    charge = stripe.Charge.create(
      amount=str(amount),
      description="Grow Bucket Kit",
      currency="usd",
      receipt_email=request.form.get('stripeEmail'),
      source=token
    )
    return render_template('checkout.html')

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
