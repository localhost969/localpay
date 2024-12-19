# LocalPay

A simple, offline-friendly payment system for NGIT students to send and receive money locally using their 12-digit roll numbers.

---

## Features

- **Sign-Up & Login**: Secure with PIN authentication.
- **Send Money**: Transfer funds easily.
- **Transaction History**: View recent transactions.
- **Balance Refresh**: Update dynamically.

---

## How to Run Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/localhost969/localpay.git
   cd localpay
   ```
2. Install dependencies:
   ```bash
   pip install flask
   ```
3. Run the app:
   ```bash
   python app.py
   ```
4. Access at `http://<your-ip>:5000` or `http://127.0.0.1:5000` on your network.
             

---

## Project Structure

```
/static       # Animations and CSS
/templates    # HTML templates
app.py        # Main application logic
/database/users.json    # User data
/database/transactions.json # Transactions data
```



