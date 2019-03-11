from flask import Flask, render_template, url_for, escape, request, redirect, session
import datetime
import pymysql

db = pymysql.connect(host='localhost', user='root', passwd='', db = 'casualJobs3')
app = Flask(__name__)
cursor = db.cursor()

@app.route('/login', methods = ['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':

        first_name = request.form['firstName']
        last_name = request.form['lastName']
        password = request.form['password']
        sql = "SELECT * from users where firstName='" + first_name + "' and lastName='" + last_name + "" + "' and password='" + password + "'"

        cursor.execute(sql)

        if cursor.fetchone() is None:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['username'] = request.form['firstName'] + " " + request.form['lastName']
            return redirect("/", code=302)

    return render_template('login.html', error=error)

@app.route('/post_job', methods = ['GET', 'POST'])
def post_job():
    
    if 'username' not in session:
        return redirect("/login", code=302)

    username = session['username']
    the_username = username.split()

    sql = "SELECT * FROM users where firstName ='" + the_username[0]  + "' and lastName='" + the_username[1] + "'"
    cursor.execute(sql)
    results = cursor.fetchall()

    user_Id = ''

    for row in results:
        user_Id = row[0]

    the_user_Id = str(user_Id)

    if request.method == 'POST':
        title =  request.form["inputTitle"]
        description =  request.form["description"]
        duration =  request.form["duration"]
        pay =  request.form["pay"]
        catagory =  request.form["catagory"]
        resources_provided = request.form["resourcesProvided"]
        resources_required = request.form["resourcesRequired"]

        phone = ""
        email = ""
        street = ""
        town = ""
        county = ""

        checked = request.form.getlist('differentContacts')
        checked2 = request.form.getlist('differentAddress')

        if checked == ['on']:
            phone = request.form["phone"]
            email = request.form["email"]    
        else:
            sql1 = "SELECT phone, email FROM users where userId =" + the_user_Id
            cursor.execute(sql)
            results2 = cursor.fetchall()
            
            for row in results2:
                phone = row[0]
                email = row[1]

        if checked2 == ['on']:
            street = request.form["street"]
            town = request.form["town"]
            county = request.form["county"] 

        else:
            sql2 = "SELECT street, town, county FROM users where userId =" + the_user_Id
            cursor.execute(sql2)
            results3 = cursor.fetchall()
            
            for row in results3:
                street = row[0]
                town = row[1]
                county = row[2]

        time_stamp_posted = datetime.datetime.now()

        cursor.execute("INSERT INTO jobs (title, UserID, description, duration, pay, catagory, timeStampPosted, resourcesProvided, resourcesRequired, email, phone, street, town, county) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (title, the_user_Id, description, duration, pay, catagory, time_stamp_posted, resources_provided, resources_required, email, phone, street, town, county))
        db.commit()

        cursor.execute("UPDATE users SET JobsPosted = JobsPosted + 1 WHERE userID = %s", (the_user_Id))
        db.commit()

        return redirect("/view_jobs", code=302)

    return render_template('postJob.html', results=results)

@app.route('/view_jobs', methods = ['GET', 'POST'])
def view_jobs():
    if 'username' in session: 
        username = session['username']
        the_username = username.split()

        sql = "SELECT * FROM users where firstName ='" + the_username[0]  + "' and lastName='" + the_username[1] + "'"
        cursor.execute(sql)
        results = cursor.fetchall()

        for row in results:
            the_user_Id = row[0]
    else:
        username = ''
        the_user_Id = 0

    sql2 = "SELECT * FROM jobs INNER JOIN users ON jobs.UserID=users.userId ORDER BY timeStampPosted DESC"
    cursor.execute(sql2)
    results2 = cursor.fetchall()
    current_time = datetime.datetime.now()
    for row in results2:
        session['job_id'] = row[2]
        elapsed_time = current_time - row[7]
    return render_template('viewJobs.html', results2 = results2, the_user_Id = the_user_Id, current_time = current_time)

@app.route('/view_job', methods = ['GET', 'POST'])
def view_job():
    
    if request.method == 'POST':
        job_id = request.form['view_button']
    
        sql = "SELECT * FROM jobs INNER JOIN users ON jobs.UserID=users.userId WHERE jobId = " + job_id
        cursor.execute(sql)
        results = cursor.fetchall()

        return render_template('viewJob.html' , results = results)
    return render_template('viewJob.html')

@app.route('/', methods = ['GET', 'POST'])
def home():
    if 'username' in session: 
        username = session['username']
    else:
        username = ''
        
    return render_template('home.html', username = username)

@app.route('/log_out', methods = ['GET', 'POST'])
def log_out():
        session.pop('username', None)
        return redirect("/", code=302)

app.secret_key = 'super secret key'
if __name__ == '__main__':
   app.run(debug = True)