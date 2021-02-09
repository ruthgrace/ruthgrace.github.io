import logging
import json
import os
import stripe
import sys
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, redirect, request, send_from_directory, jsonify
from flask_api import status
from config import testkey, prodkey, testsecretkey, prodsecretkey, testskus, prodskus

KEY = prodkey
SECRET = prodsecretkey
stripe.api_key = SECRET
COLORS = ["black", "white"]
COLOR = "white"
SKUS = prodskus
LOGDIR = '/var/log/ruthgracewong/'
LOGFILE = 'app.log'
IPHONE_SHIPPING_COST = 10
CARD = "card"

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
    stock = {}
    for c in COLORS:
        sku = SKUS[c]
        stock[c] = stripe.SKU.retrieve(sku)["inventory"]["quantity"]
    if request.method == 'GET':
        numbers = get_numbers(1, IPHONE_SHIPPING_COST)
        return render_template('iphone.html',
                               key=KEY,
                               colors=COLORS,
                               color=COLOR,
                               stock=stock,
                               cost=numbers['cost'],
                               totalcents=numbers['totalcents'],
                               totaldollars=numbers['totaldollars'],
                               stripetotal=numbers['stripetotal'])
    if request.method == 'POST':
        numbers = get_numbers(1, IPHONE_SHIPPING_COST)
        color = request.form.get('color')
        return render_template('iphone.html',
                               key=KEY,
                               colors=COLORS,
                               color=color,
                               stock=stock,
                               cost=numbers['cost'],
                               totalcents=numbers['totalcents'],
                               totaldollars=numbers['totaldollars'],
                               stripetotal=numbers['stripetotal'])

@app.route('/thankyou', methods = ['GET', 'POST'])
def thankyou():
    if request.method == 'POST':
        data = request.data
        order_data = json.loads(data)['token']
        try:
            order = stripe.Order.create(
              currency='usd',
              items=[
                {
                  "type": 'sku',
                  "parent": SKUS[order_data['color']]
                }
              ],
              shipping={
                "name": order_data[CARD]['name'],
                "address":{
                  "line1": order_data[CARD]['address_line1'],
                  "city": order_data[CARD]['address_city'],
                  "state": order_data[CARD]['address_state'],
                  "country": order_data[CARD]['address_country'],
                  "postal_code": order_data[CARD]['address_zip']
                },
              },
              email = order_data['email']
            )
            email = order_data['email']
            del order_data['color']
            del order_data['email']
            charge = stripe.Charge.create(
              amount=str(IPHONE_SHIPPING_COST * 100),
              description="Shipping for iPhone toy",
              currency="usd",
              receipt_email=email,
              source=order_data['id']
            )
            order.pay(source=order_data['id'])
            return "success"
        except stripe.error.InvalidRequestError as err:
            app.logger.warn("INVALID REQUEST ERROR: {0}".format(err))
            return jsonify({"error": str(err)}), status.HTTP_500_INTERNAL_SERVER_ERROR
    if request.method == 'GET':
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
      source=order_data['id']
    )
    return render_template('donate.html')
