from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Database paths
USERS_DB = 'database/users.json'
TRANSACTIONS_DB = 'database/transactions.json'

# PIN for admin authentication
ADMIN_PIN = '123'

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
            return jsonify({'success': False, 'message': 'User already exists!'}), 400
        # Add the new user to the users dictionary (this can be persisted to a file or database)
        users[roll_number] = {'pin': pin, 'balance': 0}  # Default balance of 0
        return jsonify({'success': True, 'message': 'User registered successfully!'})
    
    return render_template('signup.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        roll_number = request.form['roll_number']
        pin = request.form['pin']
        
        if roll_number in users and users[roll_number]['pin'] == pin:
            session['roll_number'] = roll_number
            # Check if the user is an admin
            if roll_number == 'admin':  # If admin, redirect to admin panel
                return jsonify({'success': True, 'role': 'admin'})
            else:  # Normal user, redirect to dashboard
                return jsonify({'success': True, 'role': 'user'})
        
        # If credentials are incorrect
        return jsonify({'success': False, 'message': 'Invalid login credentials!'}), 400

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
        return jsonify({"status": "error", "message": "Invalid PIN!"}), 400
    if receiver not in users:
        return jsonify({"status": "error", "message": "Receiver does not exist!"}), 400
    if users[sender]['balance'] < amount:
        return jsonify({"status": "error", "message": "Insufficient balance!"}), 400

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

    return jsonify({"status": "success", "message": "Transaction successful!"}), 200

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

@app.route('/check_receiver/', defaults={'receiver': None}, methods=['GET'])
@app.route('/check_receiver/<receiver>', methods=['GET'])
def check_receiver(receiver):
    if receiver is None:
        return jsonify({'error': 'Receiver roll number is required'}), 400  # Bad request error if no receiver is passed

    if receiver in users:
        return jsonify({'exists': True}), 200  # Receiver exists
    else:
        return jsonify({'exists': False, 'error': 'Receiver does not exist'}), 404  # Return 404 if receiver doesn't exist

@app.route('/logout')
def logout():
    session.pop('roll_number', None)
    return redirect(url_for('index'))

# Admin Routes
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    # Check if the user is logged in and is admin
    if 'roll_number' not in session or session['roll_number'] != 'admin':
        return redirect(url_for('login'))  # Redirect to login if not admin
    
    # Admin PIN verification and handling form submission
    if request.method == 'POST':
        pin = request.form['admin_pin']
        if pin != ADMIN_PIN:
            return "Invalid PIN!", 403  # Forbidden if the PIN is incorrect

    # Admin is logged in, so render the admin panel page
    return render_template('admin.html', users=users, transactions=transactions)


@app.route('/admin/update_balance', methods=['POST'])
def update_balance():
    if 'roll_number' not in session or session['roll_number'] != 'admin':
        return redirect(url_for('login'))

    # Ensure the admin enters the PIN before updating balance
    pin = request.form['admin_pin']
    if pin != ADMIN_PIN:
        return "Invalid PIN!", 403  # Forbidden if the PIN is incorrect

    # Get user data from the form
    roll_number = request.form['roll_number']
    new_balance = int(request.form['new_balance'])

    # Check if user exists
    if roll_number in users:
        users[roll_number]['balance'] = new_balance
        save_data(USERS_DB, users)
        return redirect(url_for('admin_panel'))
    else:
        return "User not found", 404

@app.route('/admin/transactions', methods=['GET'])
def admin_transactions():
    if 'roll_number' not in session or session['roll_number'] != 'admin':
        return redirect(url_for('login'))

    # Check if the admin provides the correct PIN
    if request.method == 'POST':
        pin = request.form['admin_pin']
        if pin != ADMIN_PIN:
            return "Invalid PIN!", 403  # Forbidden if the PIN is incorrect

    # Show all transactions
    return render_template('admin_transactions.html', transactions=transactions)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
