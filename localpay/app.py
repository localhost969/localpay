from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Database paths
USERS_DB = 'database/users.json'
TRANSACTIONS_DB = 'database/transactions.json'

# Load or initialize the JSON files
def load_data(file_path, default_data):
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            json.dump(default_data, file)
        return default_data
    
    if os.path.getsize(file_path) == 0:
        with open(file_path, 'w') as file:
            json.dump(default_data, file)
        return default_data

    with open(file_path, 'r') as file:
        return json.load(file)

def save_data(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

# Initialize databases
users = load_data(USERS_DB, {})
transactions = load_data(TRANSACTIONS_DB, [])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        roll_number = request.form['roll_number']
        pin = request.form['pin']
        if roll_number in users:
            return "User already exists!"
        users[roll_number] = {'pin': pin, 'balance': 0}
        save_data(USERS_DB, users)
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        roll_number = request.form['roll_number']
        pin = request.form['pin']
        if roll_number in users and users[roll_number]['pin'] == pin:
            session['roll_number'] = roll_number
            return redirect(url_for('dashboard'))
        return "Invalid login credentials!"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'roll_number' not in session:
        return redirect(url_for('login'))
    roll_number = session['roll_number']
    user = users[roll_number]
    user_transactions = [t for t in transactions if t['sender'] == roll_number or t['receiver'] == roll_number]
    return render_template('dashboard.html', user=user, transactions=user_transactions)

@app.route('/send', methods=['POST'])
def send():
    if 'roll_number' not in session:
        return redirect(url_for('login'))
    sender = session['roll_number']
    receiver = request.form['receiver']
    amount = int(request.form['amount'])
    pin = request.form['pin']

    if sender not in users or users[sender]['pin'] != pin:
        return "Invalid PIN!"
    if receiver not in users:
        return "Receiver does not exist!"
    if users[sender]['balance'] < amount:
        return "Insufficient balance!"

    # Process the transaction
    users[sender]['balance'] -= amount
    users[receiver]['balance'] += amount

    # Log the transaction
    transaction = {
        'sender': sender,
        'receiver': receiver,
        'amount': amount,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    transactions.append(transaction)
    save_data(USERS_DB, users)
    save_data(TRANSACTIONS_DB, transactions)

    return jsonify({"status": "success"}), 200

@app.route('/balance', methods=['GET'])
def get_balance():
    if 'roll_number' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    roll_number = session['roll_number']
    balance = users[roll_number]['balance']
    return jsonify({'balance': balance}), 200

@app.route('/transactions', methods=['GET'])
def get_transactions():
    if 'roll_number' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    roll_number = session['roll_number']
    user_transactions = [t for t in transactions if t['sender'] == roll_number or t['receiver'] == roll_number]
    return jsonify({'transactions': user_transactions}), 200

@app.route('/logout')
def logout():
    session.pop('roll_number', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

