import datetime
from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2
import psycopg2.extras

#To loggout -------> session.pop('loggedin', None)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'

conn = psycopg2.connect(host = "localhost", dbname = "fitness", user = "postgres", password = "Michaelm82!", port = 5433) 
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

@app.route('/')
def home():
    if 'loggedin' in session:
        return render_template('home.html', variable = session['first_name'])
    else:
        return redirect(url_for('login'))

@app.route('/signup', methods = ['GET', 'POST'])
def register():    
    if request.method == 'POST':
        username = request.form.get('username')
        cur.execute('SELECT * FROM users WHERE user_name = %s', (username,))
        account = cur.fetchone()
        if account is None:
            password = request.form.get('password')
            password2 = request.form.get('password2')
            first_name = request.form.get('firstname')
            last_name = request.form.get('lastname')
        else:
            flash("Username already exists", category = 'error')
        if password != password2:
            flash("Passwords do not match!", category = 'error')
        else:
            cur.execute("INSERT INTO users (user_name, password, first_name, last_name) VALUES (%s, %s, %s, %s);", (username,  password, first_name, last_name))
            conn.commit()
            flash("Account Created!", category = 'Success')
    return render_template('register.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        cur.execute("SELECT * FROM users WHERE user_name = %s", (username,))
        account = cur.fetchone()
        if (not account):
            flash("Username does not exist", category = 'error')
        elif password != account["password"]:
            flash("Password is incorrect!", category = 'error')
        else:
            session['loggedin'] = True
            session['username'] = account['user_name']
            session['first_name'] = account['first_name']
            session['last_name'] = account['last_name']
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/goalInput', methods = ['GET', 'POST'])
def goalInput():
    if 'loggedin' in session:
        cur.execute("select exists(select goal_weight from goal where user_name = %s)", (session['username'],))
        goal_exists = cur.fetchone()[0]
        if (goal_exists == True):
            cur.execute('SELECT goal_weight, goal_date from goal where user_name = %s', (session['username'],))
            goal = cur.fetchone()
            session['goal_weight'] = goal['goal_weight']
            session['goal_date'] = goal['goal_date']
            return redirect(url_for('goal'))
        if request.method == 'POST':
            session['goal_weight'] = request.form.get('goal_weight')
            session['goal_date'] = request.form.get('goal_date')
            cur.execute("INSERT INTO goal (user_name, goal_weight, goal_date) VALUES (%s, %s, %s);", (session['username'],  session['goal_weight'], session['goal_date']))
            conn.commit()
            return redirect(url_for('goal'))
    else:
        return redirect(url_for('login'))
    return render_template('goalInput.html')

@app.route('/goal')
def goal():
    return render_template('goal.html', weight = session['goal_weight'], date = session['goal_date'])

@app.route('/progress', methods = ['GET', 'POST'])
def progress():
    if 'loggedin' in session:
        if request.method == 'POST':    
            progress_weight = request.form.get('progress_weight')
            progress_date = request.form.get('progress_date')
            cur.execute("INSERT INTO progress (user_name, progress_weight, progress_date) VALUES (%s, %s, %s);", (session['username'],  progress_weight, progress_date))
            conn.commit()
            cur.execute("SELECT progress_weight, progress_date FROM progress WHERE user_name = %s", (session['username'],))
            progress = cur.fetchall()
            return render_template('progress.html', goal_weight = session['goal_weight'], goal_date = session['goal_date'], progress = progress)
    else:
        return redirect(url_for('login'))
    return render_template('progress.html')

@app.route('/fitness', methods = ['GET', 'POST'])
def fitness():
    if 'loggedin' in session:
        if request.method == 'POST':
            fitness_activity = request.form.get("fitness_activity")
            fitness_time = request.form.get("fitness_time")
            cur.execute("INSERT INTO activities (user_name, activity, time_length) VALUES (%s, %s, %s);", (session['username'],  fitness_activity, fitness_time))
            conn.commit()
            cur.execute("SELECT activity, time_length FROM activities WHERE user_name = %s", (session['username'],))
            activity = cur.fetchall()
            return render_template('fitness.html', activity = activity)
    else:
        return redirect(url_for('login'))
    return render_template('fitness.html')
@app.route('/nutrition', methods = ['GET', 'POST'])
def nutrition():
    if 'loggedin' in session:
        cur.execute("SELECT food_name FROM nutrition")
        food_names = cur.fetchall()
        if request.method == 'POST':
            current_date = datetime.date.today()
            food_input = request.form.get("food_input")
            cur.execute("SELECT calories, total_fat, carbohydrates FROM nutrition WHERE food_name = %s", (food_input,))
            food_info = cur.fetchone()
            print(food_info)
            cur.execute("INSERT INTO user_nutrition (username, food_name, calories, total_fat, carbohydrates, date) VALUES (%s, %s, %s, %s, %s, %s);", (session['username'], food_input, food_info['calories'], food_info['total_fat'], food_info['carbohydrates'], current_date))
            conn.commit()
            cur.execute("SELECT food_name, calories, total_fat, carbohydrates, date FROM user_nutrition WHERE username = %s", (session['username'],))
            user_food = cur.fetchall()
            return render_template('nutrition.html', food_names = food_names, food_info = user_food) 
    else:
        return redirect(url_for('login'))
    return render_template('nutrition.html',food_names = food_names)

@app.route('/loggout')
def loggout():
    session.pop('username', None)
    session.pop('first_name', None)
    session.pop('last_name', None)
    session.pop('goal_weight', None)
    session.pop('goal_date', None)
    session['loggedin'] = False
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)