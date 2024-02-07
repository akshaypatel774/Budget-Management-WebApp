# app.py
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget.db'
db = SQLAlchemy(app)

class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_budget = db.Column(db.Float, default=0.0)
    transactions = db.relationship('Transaction', backref='budget', lazy=True)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=False)
    transaction_type = db.Column(db.String(10), nullable=False)
    budget_id = db.Column(db.Integer, db.ForeignKey('budget.id'), nullable=False)

@app.route('/')
def index():
    budget = Budget.query.first()
    return render_template('index.html', budget=budget)

@app.route('/set_budget', methods=['POST'])
def set_budget():
    total_budget = float(request.form.get('total_budget'))
    budget = Budget.query.first()
    if budget:
        budget.total_budget = total_budget
    else:
        budget = Budget(total_budget=total_budget)
        db.session.add(budget)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/set_budget')
def set_budget_page():
    return render_template('set_budget.html')

@app.route('/add_transaction', methods=['POST'])
def add_transaction():
    amount = float(request.form.get('amount'))
    description = request.form.get('description')
    transaction_type = request.form.get('transaction_type')
    budget = Budget.query.first()

    if transaction_type == 'income':
        budget.total_budget += amount
    elif transaction_type == 'expense':
        budget.total_budget -= amount

    transaction = Transaction(amount=amount, description=description, transaction_type=transaction_type, budget=budget)
    db.session.add(transaction)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/delete_transaction/<int:transaction_id>')
def delete_transaction(transaction_id):
    transaction = Transaction.query.get(transaction_id)
    if transaction:
        budget = Budget.query.first()
        if transaction.transaction_type == 'income':
            budget.total_budget -= transaction.amount
        elif transaction.transaction_type == 'expense':
            budget.total_budget += transaction.amount

        db.session.delete(transaction)
        db.session.commit()

    return redirect(url_for('list'))

@app.route('/list')
def list():
    budget = Budget.query.first()
    income_transactions = Transaction.query.filter_by(transaction_type='income').all()
    expense_transactions = Transaction.query.filter_by(transaction_type='expense').all()

    total_income = sum(income.amount for income in income_transactions)
    total_expense = sum(expense.amount for expense in expense_transactions)

    return render_template('list.html', budget=budget, income_transactions=income_transactions, expense_transactions=expense_transactions, total_income=total_income, total_expense=total_expense)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
