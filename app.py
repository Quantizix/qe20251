from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "some_secret_key"  # For session management

# -----------------------
# USER & AUTH SETUP
# -----------------------
users = {
    "admin": "adminpass"
}
SIGNUP_CODE = "quantest"  # Only people who know this can sign up

# -----------------------
# MACROS STORAGE
# -----------------------
macros_data = []
# each entry:
# {
#   "username": "...",
#   "date": "YYYY-MM-DD",
#   "food": "...",
#   "calories": "...",
#   "protein": "...",
#   "fat": "...",
#   "carbs": "..."
# }

# -----------------------
# TIME BLOCKS STORAGE
# -----------------------
timeblocks_data = []
# each entry:
# {
#   "username": "...",
#   "date": "YYYY-MM-DD",
#   "blocks": {
#       "00:00-01:00": "User input",
#       "01:00-02:00": "User input",
#       ...
#       "23:00-00:00": "User input"
#    }
# }

# -----------------------
# REMINDERS STORAGE
# -----------------------
reminders_data = []
# each entry:
# {
#   "username": "...",
#   "date": "YYYY-MM-DD",
#   "reminder_text": "..."
# }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in users and users[username] == password:
            session['username'] = username
            # If admin logs in, go to admin page
            if username == 'admin':
                return redirect(url_for('admin'))
            else:
                # Regular user -> home page
                return redirect(url_for('index'))
        else:
            return "Invalid credentials. <a href='/login'>Try again</a>"

    # GET -> show login form
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        code = request.form.get('signup_code')
        username = request.form.get('username')
        password = request.form.get('password')

        if code == SIGNUP_CODE:
            if username not in users:
                users[username] = password
                return "Sign Up successful! <a href='/login'>Login now</a>"
            else:
                return "Username already exists. <a href='/signup'>Try another</a>"
        else:
            return "Invalid sign-up code. <a href='/signup'>Try again</a>"

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    # Only admin user can see this page
    if 'username' in session and session['username'] == 'admin':
        return render_template('admin.html')
    else:
        return "Access Denied"

# -----------------------
# MACROS
# -----------------------
macros_data = []

@app.route('/macros', methods=['GET', 'POST'])
def macros():
    if 'username' not in session:
        return "Please <a href='/login'>Login</a>"

    if request.method == 'POST':
        # Automatically store the current date/time
        datetime_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        food = request.form.get('food')
        calories = request.form.get('calories')
        protein = request.form.get('protein')
        fat = request.form.get('fat')
        carbs = request.form.get('carbs')

        entry = {
            'username': session['username'],
            'date': datetime_str,  # we store the exact date & time
            'food': food,
            'calories': calories,
            'protein': protein,
            'fat': fat,
            'carbs': carbs
        }
        macros_data.append(entry)

    user_macros = [m for m in macros_data if m['username'] == session['username']]

    return render_template('macros.html', macros_list=user_macros)

# -----------------------
# TIME BLOCKS
# -----------------------
from datetime import datetime

timeblocks_data = []

@app.route('/timeblocks', methods=['GET', 'POST'])
def timeblocks():
    if 'username' not in session:
        return "Please <a href='/login'>Login</a> to access time blocks."

    if request.method == 'POST':
        # Automatically use today's date (e.g., "2024-12-20")
        date_str = datetime.now().strftime("%Y-%m-%d")

        blocks_dict = {}
        for i in range(24):
            # label like "0:00", "1:00", etc.
            label = f"{i}:00"
            user_input = request.form.get(f"block_{i}")
            blocks_dict[label] = user_input if user_input else ""

        entry = {
            'username': session['username'],
            'date': date_str,
            'blocks': blocks_dict
        }
        timeblocks_data.append(entry)

    user_blocks = [tb for tb in timeblocks_data if tb['username'] == session['username']]

    return render_template('timeblocks.html', user_blocks=user_blocks)

# -----------------------
# REMINDERS
# -----------------------
@app.route('/reminders', methods=['GET', 'POST'])
def reminders():
    if 'username' not in session:
        return "Please <a href='/login'>Login</a> first."

    if request.method == 'POST':
        date_str = request.form.get('date')  # user picks a date
        reminder_text = request.form.get('reminder_text')

        entry = {
            'username': session['username'],
            'date': date_str,
            'reminder_text': reminder_text
        }
        reminders_data.append(entry)

    # Only show data for this user
    user_reminders = [r for r in reminders_data if r['username'] == session['username']]
    return render_template('reminders.html', reminders_list=user_reminders)

# -----------------------
# OTHER
# -----------------------
@app.route('/other')
def other():
    if 'username' not in session:
        return "Please <a href='/login'>Login</a> first."
    return render_template('other.html')


# -----------------------
# RUN FLASK
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)
