import csv
from io import StringIO
from flask import Flask, render_template, request, redirect, Response
from sqlalchemy import create_engine, text

db_connection_string = "mysql+pymysql://mubmtot7duua3rs38pez:pscale_pw_Nl22GjWxCL800T3NIty11DyYgoV53xZVtnpVEcWW33z@aws.connect.psdb.cloud/ssc_att?charset=utf8mb4"
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
        stmt = text("INSERT INTO SST_ATT_NEW_TBL_1 (nm, Lnm, ip) VALUES (:full_name, :last_name, :ip_address)")
        full_name = data.get('Full_name')
        last_name = data.get('Lnm')
        ip_address = request.remote_addr
        conn.execute(stmt, {'full_name': full_name, 'last_name': last_name, 'ip_address': ip_address})


# Retrieve existing values from the database
def get_existing_values():
    with engine.connect() as conn:
        stmt = text("SELECT DISTINCT last_name FROM SST_ATT_NEW_TBL_1")
        result = conn.execute(stmt)
        existing_values = [row[0] for row in result]
    return existing_values


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
        add_application_to_db(data)
        return redirect("/home")

    last_names = get_existing_values()

    delete_success = request.args.get('delete_success')
    if delete_success == 'true':
        message = "Deletion successful"
    else:
        message = None

    data = execute_sql_statement()
    return render_template("home.html", message=message, data=data, last_names=last_names)


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


# Delete route
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


# Export to CSV
@app.route("/export")
def export_csv():
    data = execute_sql_statement()
    # Create a CSV response
    def generate_csv():
        csv_data = [['ID', 'Full Name', 'Last Name', 'IP Address', 'Date/Time']]
        csv_data.extend([[row.id, row.full_name, row.last_name, row.ip, row.created_at] for row in data])
        csv_file = StringIO()
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)
        csv_file.seek(0)
        yield from csv_file
    return Response(generate_csv(), mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=values.csv'})


# Approve route
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


@app.route("/showvalue")
def showvalue():
    data = execute_sql_statement()
    return render_template("home.html", data=data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
