# LocalPay

A simple, offline-friendly payment system for NGIT students to send and receive money locally using their 12-digit roll numbers.
![image](https://github.com/user-attachments/assets/2c902854-b2e6-42a6-ac2f-af376546151b)
![image](https://github.com/user-attachments/assets/6807fa27-d0cd-4782-882d-f626c01503b1)
![image](https://github.com/user-attachments/assets/2fa99d8d-7831-4993-8493-05d5f1d688e3)
![image](https://github.com/user-attachments/assets/718d2f8c-3ce2-4c71-b186-12ec849e2ef7)







---

## Features

- **Sign-Up & Login**: Secure with PIN authentication.
- **Send Money**: Transfer funds easily.
- **Transaction History**: View recent transactions.
- **Balance Refresh**: Update dynamically.
- **Admin Panel**: Admin can moniter users.
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



