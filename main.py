import csv
from io import StringIO
from flask import Flask, render_template, request, redirect, Response
from sqlalchemy import create_engine, text

db_connection_string = "mysql+pymysql://mtclbbq14rgbqg4kmn0w:pscale_pw_vm49ycJaPR4t9baizkpsOOWj16RDben3qLu5eRn4XVo@aws.connect.psdb.cloud/ssc_att?charset=utf8mb4"
engine = create_engine(db_connection_string, connect_args={"ssl": {"ssl_ca": "/etc/ssl/cert.pem"}})
app = Flask(__name__)

def verify_password(username, password):
    with engine.connect() as conn:
        stmt = text("SELECT COUNT(*) FROM sst_password WHERE username = :username AND password = :password")
        result = conn.execute(stmt, {"username": username, "password": password})
        count = result.scalar()
        return count > 0

@app.route("/")
def login_form():
    return render_template("login.html", error_message="")

@app.route("/login", methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    # Verify the password against the database
    if verify_password(username, password):
        # Authentication successful, redirect to home page
        return redirect("/home")
    else:
        # Authentication failed, show error message
        return render_template("login.html", error_message="Invalid username or password")

# Add application to database
def add_application_to_db(data):
    with engine.connect() as conn:
        stmt = text("INSERT INTO SST_ATT_NEW_TBL_1 (nm, ip, Lnm) VALUES (:name, :ip_address, :Lnm)")
        values = [{'name': name, 'Lnm': Lnm, 'ip_address': request.remote_addr} for name, Lnm in data.lists()]
        conn.execute(stmt, values)

  
# Retrieve existing values from the database
    with engine.connect() as conn:
        stmt = text("SELECT DISTINCT Lnm FROM SST_ATT_NEW_TBL_1")
        result = conn.execute(stmt)
        existing_values = [row[0] for row in result]


    return render_template('home.html', existing_values=existing_values)
# Delete application from database
def delete_application_from_db(row_id):
    with engine.connect() as conn:
        stmt = text("DELETE FROM SST_ATT_NEW_TBL_1 WHERE id = :row_id")
        conn.execute(stmt, {'row_id': row_id})

# Update status to 'Approved' in the database
def update_status_to_approved(row_id):
    with engine.connect() as conn:
        stmt = text("UPDATE SST_ATT_NEW_TBL_1 SET status = 'Approved' WHERE id = :row_id")
        conn.execute(stmt, {'row_id': row_id})

# Execute SQL statement
def execute_sql_statement():
    with engine.connect() as conn:
        stmt = text("SELECT * FROM SST_ATT_NEW_TBL_1 ORDER BY id DESC")
        result = conn.execute(stmt)
        return result.fetchall()

@app.route("/home", methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        data = request.form
        full_name = add_application_to_db(data)
        # Process the form data and add to the database

    # Retrieve last names from the database
    with engine.connect() as conn:
        stmt = text("SELECT distinct Lnm FROM SST_ATT_NEW_TBL_1")
        result = conn.execute(stmt)
        last_names = [row[0] for row in result]

    




    delete_success = request.args.get('delete_success')
    if delete_success == 'true':
        message = "Deletion successful"
    else:
        message = None

    data = execute_sql_statement()
    return render_template("home.html", message=message, data=data, last_names=last_names)


  
@app.route("/delete", methods=['POST'])

def delete():
    row_id = request.form.get('id')
    if row_id:
        try:
            delete_application_from_db(row_id)
            return redirect("/home?delete_success=true")
        except Exception as e:
            print(e)
            return "Failed to delete. Please try again later."
    else:
        return "Invalid request"



from flask import Flask, render_template, request, redirect, Response
from sqlalchemy import create_engine, text
# ... (existing code omitted for brevity)
# Export to CSV
@app.route("/export")
def export_csv():
    data = execute_sql_statement()
    # Create a CSV response
    def generate_csv():
        csv_data = [['ID', 'Name', 'IP Address', 'Date/Time']]
        csv_data.extend([[row.id, row.nm, row.ip, row.created_at] for row in data])
        csv_file = StringIO()
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)
        csv_file.seek(0)
        yield from csv_file
    return Response(generate_csv(), mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=values.csv'})

@app.route("/approve", methods=['POST'])
def approve():
    row_id = request.form.get('id')
    if row_id:
        try:
            update_status_to_approved(row_id)
            return redirect("/home")
        except Exception as e:
            print(e)
            return "Failed to approve. Please try again later."
    else:
        return "Invalid request"


# Showvalue page

@app.route("/showvalue")
def showvalue():
    data = execute_sql_statement()
    return render_template("home.html", data=data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)