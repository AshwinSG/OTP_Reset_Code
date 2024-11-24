from flask import Flask, render_template, request, session
import random
import sqlite3
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'


@app.route('/')
def index():
    users = get_user_data_from_database()
    return render_template('index.html', users=users)

def get_user_data_from_database():
    try:
        conn = sqlite3.connect('user_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT username, password, email, reset_code, try_box FROM users")
        users = cursor.fetchall()
        return users
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return []
    finally:
        conn.close()

@app.route('/reset1', methods=['GET', 'POST'])
def reset_submit():
    if request.method == 'POST':
        otp = generate_otp()
        email = request.form.get('email')
        if send_otp_email(otp, email):
            session['reset_otp'] = otp
            update_reset_code_and_try_box_in_database(email, otp)
            return render_template('reset2.html')
        else:
            return render_template('reset1.html')
    return render_template('reset1.html')

@app.route('/reset2', methods=['GET', 'POST'])
def update_password_submit():
    if request.method == 'POST':
        email = request.form.get('email')
        reset_code = request.form.get('reset_code')
        print(email)
        print(reset_code)
        if check_email_reset_code(email, reset_code):
            session['email_used'] = email
            return render_template('reset3.html')
        else:
            return "Invalid reset code or Try Box is not 0. Password cannot be updated."
    return render_template('reset2.html')

@app.route('/reset3', methods=['GET', 'POST'])
def reset1():
    return render_template('reset1.html')

@app.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        new_password = request.form.get('textInput')
        email = session.get('email_used')
        if email:
            update_password_in_database(email, new_password)
            return render_template('change_password.html')
        else:
            return "Session expired. Please try again."
    return render_template('change_password.html')

def generate_otp():
    return ''.join(str(random.randint(0, 9)) for _ in range(6))

def send_otp_email(otp, email):
    sender_email = "sbatchu5@gitam.in"
    password = "Ashwin123@"
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email
    msg['Subject'] = "Password Reset OTP - NPR"
    body = "This is the OTP for password reset: " + otp
    msg.attach(MIMEText(body, 'plain'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, password)
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print("Failed to send email:", e)
        return False

def update_reset_code_and_try_box_in_database(email, otp):
    conn = sqlite3.connect('user_database.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET reset_code=?, try_box=? WHERE email=?", (otp, 0, email))
    conn.commit()
    conn.close()

def check_email_reset_code(email, reset_code):
    try:
        conn = sqlite3.connect('user_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT reset_code FROM users WHERE email=?", (email,))
        result = cursor.fetchone()
        print(result)
        if str(result[0]) == str(reset_code):
            print("True is called")
            return True
        return False
    except sqlite3.Error as e:
        print("SQLite error:", e)
        return False
    finally:
        conn.close()

def update_password_in_database(email, new_password):
    try:
        conn = sqlite3.connect('user_database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ?, reset_code = ?, try_box = ? WHERE email = ?", 
                       (new_password, 0, 1, email))
        conn.commit()
    except sqlite3.Error as e:
        print("SQLite error:", e)
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
