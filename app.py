from flask import Flask, render_template, request, redirect, url_for, session
from models import init_db, get_user, get_events, add_event
from functools import wraps
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'dtims_events'
}

app = Flask(__name__)
app.secret_key = 'your_secret_key'
init_db()

def role_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                return redirect('/')
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = get_user(username, password)
    if user:
        session['username'] = user['username']
        session['role'] = user['role']
        return redirect(url_for('dashboard'))
    else:
        return "Invalid credentials"

@app.route('/dashboard')
def dashboard():
    if 'role' not in session:
        return redirect('/')
    role = session['role']
    events = get_events()
    return render_template(f'{role}_dashboard.html', events=events)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/add_expense', methods=['GET', 'POST'])
@role_required('management_student')
def add_expense():
    if request.method == 'POST':
        event_id = request.form['event_id']
        item = request.form['item']
        cost = request.form['cost']
        added_by = session['username']
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (event_id, item, cost, added_by) VALUES (%s, %s, %s, %s)", (event_id, item, cost, added_by))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('add_expense.html')
@app.route('/mark_attendance', methods=['GET', 'POST'])
@role_required('teacher')
def mark_attendance():
    if request.method == 'POST':
        event_id = request.form['event_id']
        student_name = request.form['student_name']
        status = request.form['status']
        marked_by = session['username']
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO attendance (event_id, student_name, status, marked_by) VALUES (%s, %s, %s, %s)", (event_id, student_name, status, marked_by))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('mark_attendance.html')
@app.route('/submit_feedback', methods=['GET', 'POST'])
@role_required('student')
def submit_feedback():
    if request.method == 'POST':
        event_id = request.form['event_id']
        student_name = session['username']
        comments = request.form['comments']
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO feedback (event_id, student_name, comments) VALUES (%s, %s, %s)", (event_id, student_name, comments))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))
    return render_template('submit_feedback.html')
if __name__ == '__main__':
    app.run(debug=True)