import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os

# ACCESS_KEY = "78421e11c87b30aca160257edc630b34"
ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY')

endpoint = "http://api.marketstack.com/v2/eod/latest"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = SECRET_KEY

db = SQLAlchemy(app)

Bootstrap5(app)

class Stock(db.Model):
    name = db.Column(db.String(50), nullable=False)
    open = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    symbol = db.Column(db.String(50), nullable=False, primary_key=True)
    volume = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    exchange_code = db.Column(db.String(20), nullable=False)
    price_currency = db.Column(db.String(20), nullable=False)


class StockForm(FlaskForm):
    symbol = StringField('Symbol', validators=[DataRequired()])
    submit = SubmitField('Submit')

with app.app_context():
    db.create_all()

def fetch_stock(symbol):
    response = requests.get(endpoint, params={'access_key': ACCESS_KEY, 'symbols': symbol})
    data = response.json()
    data = data['data'][0]
    # print(data)
    return data


@app.route('/')
def home():
    stocks = db.session.execute(db.select(Stock))
    stocks = stocks.scalars().all()
    # print(stocks)
    return render_template('home.html', stocks=stocks)

@app.route('/add', methods=['POST', 'GET'])
def add():
    form = StockForm()
    if form.validate_on_submit():
        symbol = form.symbol.data
        # print(symbol)
        data = fetch_stock(symbol)
        new_data = Stock(
            name=data['name'],
            open=data['open'],
            close=data['close'],
            price_currency=data['price_currency'],
            exchange_code=data['exchange_code'],
            high=data['high'],
            low=data['low'],
            volume=data['volume'],
            symbol=data['symbol']
        )
        db.session.add(new_data)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html', form=form)

@app.route('/delete/<string:symbol>')
def delete_stock(symbol):
    stock_to_delete = db.get_or_404(Stock, symbol)
    db.session.delete(stock_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/update/<string:symbol>')
def update_stocks(symbol):
    stock_to_update = db.get_or_404(Stock, symbol)
    # print(stock_to_update)
    data = fetch_stock(stock_to_update.symbol)
    stock_to_update.open = data['open']
    stock_to_update.close = data['close']
    stock_to_update.volume = data['volume']
    stock_to_update.high = data['high']
    stock_to_update.low = data['low']
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/details/<string:symbol>')
def details(symbol):
    stock = db.get_or_404(Stock, symbol)
    return render_template('details.html', stock=stock)

if __name__ == '__main__':
    app.run(debug=True)
