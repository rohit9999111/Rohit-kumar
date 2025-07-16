from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os

def init_db():
    database_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
    conn = sqlite3.connect(database_path)
    c = conn.cursor()
    # Continue as usual...

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from functools import wraps





from flask import Flask, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set a secure secret key

# Your routes and logic go here



app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Database initialization function (you've already implemented this)
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT,
                    isVoted BOOLEAN DEFAULT FALSE

                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS votes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    candidate TEXT
                )''')
    conn.commit()
    conn.close()

# Decorator to require login for certain routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            flash('Login successful!', 'success')
            return redirect(url_for('vote'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists. Please choose a different one.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():

    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT isVoted FROM users WHERE id = ?', (session['user_id'],))
    user = c.fetchone()
    conn.close()

    # Check if the user has already voted in this session
    
    
    if user and user[0]:  # If isVoted is True
        flash('You have already voted', 'danger')
        return redirect(url_for('results'))
    
    if request.method == 'POST':
        candidate = request.form.get('candidate')  # Get the selected candidate
        if candidate:
            user_id = session['user_id']  # Assume user ID is stored in session upon login
            
            # Insert the vote into the database
            conn = sqlite3.connect('db.sqlite3')
            c = conn.cursor()
            try:
                c.execute('INSERT INTO votes (user_id, candidate) VALUES (?, ?)', (user_id, candidate))
                c.execute('UPDATE users SET isVoted = TRUE WHERE id = ?', (user_id,))
                conn.commit()
                conn.close()
                

                # Mark the session as voted
                session['voted'] = True
                flash('Your vote has been cast!', 'success')
                return redirect(url_for('results'))
            except sqlite3.Error as e:
                conn.rollback()
                print(f"Database error: {e}")
                flash('An error occurred. Please try again.', 'danger')
                return redirect(url_for('vote'))
        else:
            flash('Please select a candidate to vote for.', 'warning')

    # Render the voting page if they haven't voted yet
    return render_template('vote.html')

# Results page
@app.route('/results')
@login_required
def results():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT candidate, COUNT(*) as vote_count FROM votes GROUP BY candidate')
    results = c.fetchall()
    conn.close()

    return render_template('results.html', results=results)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database setup
def init_db():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            candidate TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Route: Home Page
@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/logout')
# def logout():
#     session.pop('user_id', None)
#     flash('You have been logged out.')
#     return redirect(url_for('index'))
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    session.pop('voted', None)  # Clear voting status from session
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))




# Route: Voting Page
@app.route('/vote', methods=['GET', 'POST'])
@login_required  # Protect the route so only logged-in users can access it
def vote():
    print(f"Session voted: {session.get('voted', False)}")

    if 'voted' in session and session['voted']:  # Check if the user has already voted
        flash('You have already voted in this session. Please log in again to vote.', 'danger')
        return redirect(url_for('results'))  # Redirect to results page if they already voted

    if request.method == 'POST':
        candidate = request.form['candidate']  # Get the selected candidate
        user_id = session['user_id']  # Get the logged-in user's ID

        # Store vote in the database
        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        c.execute('INSERT INTO votes (user_id, candidate) VALUES (?, ?)', (user_id, candidate))
        conn.commit()
        conn.close()

        # Mark the session as voted
        session['voted'] = True
        flash('Your vote has been cast!', 'success')
        return redirect(url_for('results'))  # Redirect to results page after voting

    # Render the voting page if they haven't voted yet
    return render_template('vote.html')

#lohout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    session.pop('voted', None)  # Clear voting status from session
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# Route: Voting Results
@app.route('/results')
def results():
    conn = sqlite3.connect('db.sqlite3')
    c = conn.cursor()
    c.execute('SELECT candidate, COUNT(*) as vote_count FROM votes GROUP BY candidate')
    results = c.fetchall()
    conn.close()

    return render_template('results.html', results=results)

# Route: Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            return redirect(url_for('vote'))
        else:
            flash('Invalid credentials!')

    return render_template('login.html')

# Route: Register Page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('db.sqlite3')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            flash('Registered successfully! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists!')

        conn.close()

    return render_template('register.html')

if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)



