from flask import Flask, request, redirect, url_for, render_template
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import logging
import warnings

# Set up warning configuration
warnings.simplefilter('always')  # Ensure warnings are always shown

# Set up logging configuration
logging.basicConfig(level=logging.DEBUG)  # Log all messages of level DEBUG and above

app = Flask(__name__)
app.secret_key = 'temporary_key'

def get_db_connection():
    logging.debug("Connecting to the database...")  # Debug log for database connection
    try:
        conn = mysql.connector.connect(
            host='clonedb.cp4g68msmepl.us-east-1.rds.amazonaws.com',
            user='admin',
            password='qwertyuiop12345asdfghjkl;',
            database='clone_db'
        )
        logging.debug("Database connection successful")
        return conn
    except mysql.connector.Error as err:
        logging.error(f"Error connecting to database: {err}")
        return None

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='sha256')

        conn = get_db_connection()
        if conn is None:
            return "Database connection failed", 500
        
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, password_hash) VALUES (%s, %s)',
            (username, hashed_password)
        )
        conn.commit()
        cursor.close()
        conn.close()

        logging.info(f"New user registered: {username}")
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        if conn is None:
            return "Database connection failed", 500
        
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM users WHERE username = %s', (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result and check_password_hash(result[0], password):
            logging.info(f"User {username} logged in successfully.")
            return redirect(url_for('dashboard'))
        else:
            logging.warning(f"Failed login attempt for user: {username}")
            return 'Invalid credentials', 401
    return render_template('login.html')


# Dashboard Route (after login)
@app.route('/dashboard')
def dashboard():
    course_urls = [
        'https://clonebucker8.s3.us-east-1.amazonaws.com/python_code.pdf',
        'https://clonebucker8.s3.us-east-1.amazonaws.com/PYTHON%2BPROGRAMMING%2BNOTES.pdf'
    ]
    
    return render_template('dashboard.html', course_urls=course_urls)

# Home Route (Landing Page)
@app.route('/')
def home():
    return render_template('home.html')

# Logout
@app.route('/logout')
def logout():
    logging.info("User logged out.")
    return redirect(url_for('login'))


if __name__ == '__main__':  # Correct the typo: use '__main__' instead of '_main_'
    app.run(host="0.0.0.0", port=5000, debug=True)
