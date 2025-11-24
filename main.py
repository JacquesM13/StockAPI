import requests
from flask import Flask, render_template, request, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

ACCESS_KEY = ""
endpoint = "http://api.marketstack.com/v2/eod/latest"

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

def fetch_stock(symbol):
    response = requests.get(endpoint, params={'access_key': ACCESS_KEY, 'symbols': symbol})
    data = response.json()
    data = data['data'][0]
    return data


@app.route('/')
def home():
    stocks = db.session.execute(db.select(Stock))
    stocks = stocks.scalars().all()
    print(stocks)
    return render_template('home.html', stocks=stocks)

@app.route('/add', methods=['POST', 'GET'])
def add():
    form = StockForm()
    if form.validate_on_submit():
        symbol = form.symbol.data
        print(symbol)
        data = fetch_stock(symbol)
        new_data = Stock(
            name=data['name'],
            open=data['open'],
            close=data['close'],
            symbol=data['symbol']
        )
        db.session.add(new_data)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
