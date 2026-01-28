from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)

# This creates a database file named 'expenses.db' automatically
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

# Initialize the database
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    view = request.args.get('view', 'daily')
    now = datetime.utcnow()
    
    # Filter logic for Daily, Weekly, Monthly
    if view == 'weekly':
        start_date = now - timedelta(days=7)
    elif view == 'monthly':
        start_date = now - timedelta(days=30)
    else:
        # Daily: from the start of today
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)

    expenses = Expense.query.filter(Expense.date >= start_date).order_by(Expense.date.desc()).all()
    total = sum(e.amount for e in expenses)
    
    return render_template('index.html', expenses=expenses, total=total, view=view)

@app.route('/add', methods=['POST'])
def add_expense():
    item = request.form.get('item')
    amount = request.form.get('amount')
    category = request.form.get('category')
    
    if item and amount:
        new_expense = Expense(item=item, amount=float(amount), category=category)
        db.session.add(new_expense)
        db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)