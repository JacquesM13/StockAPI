import requests
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# ACCESS_KEY = ""
# endpoint = "http://api.marketstack.com/v2/eod/latest"
#
# params = {"access_key": ACCESS_KEY,
#           "symbols": "AAPL"}
#
# response = requests.get(endpoint, params=params)
# response.raise_for_status()
# data = response.json()
data = {'pagination': {'limit': 100, 'offset': 0, 'count': 1, 'total': 1}, 'data': [{'open': 265.95, 'high': 273.33, 'low': 265.67, 'close': 271.49, 'volume': 58784100.0, 'adj_high': 273.33, 'adj_low': 265.67, 'adj_close': 271.49, 'adj_open': 265.95, 'adj_volume': 59030832.0, 'split_factor': 1.0, 'dividend': 0.0, 'name': 'Apple Inc', 'exchange_code': 'NASDAQ', 'asset_type': 'Stock', 'price_currency': 'USD', 'symbol': 'AAPL', 'exchange': 'XNAS', 'date': '2025-11-21T00:00:00+0000'}]}
data = data['data'][0]
print(data)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movie_database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = ''

db = SQLAlchemy(app)

Bootstrap5(app)

class Stock(db.Model):
    name = db.Column(db.String(50), primary_key=True)
    open = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    symbol = db.Column(db.String(50), nullable=False)

class StockForm(FlaskForm):
    symbol = StringField('Symbol', validators=[DataRequired()])
    submit = SubmitField('Submit')

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html', data=data)

@app.route('/add', methods=['POST', 'GET'])
def add():
    form = StockForm()
    if form.validate_on_submit():
        symbol = form.symbol.data
    #     Add a bit here that calls the API
    return render_template('add.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
