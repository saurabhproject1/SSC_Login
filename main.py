from flask import Flask, render_template, request
from sqlalchemy import create_engine, text

db_connection_string = "mysql+pymysql://9q5hmn3z07sg04w2hnbo:pscale_pw_DyoLxwHaohN2Sc1Kb3xW6S8uMP749buFS0sHjFlDjGF@aws.connect.psdb.cloud/ssc_att?charset=utf8mb4"

engine = create_engine(
    db_connection_string,
    connect_args={
        "ssl": {
            "ssl_ca": "/etc/ssl/cert.pem"
        }
    }
)

app = Flask(__name__)


def add_application_to_db(data):
    with engine.connect() as conn:
        stmt = text("INSERT INTO SSC_ATT_TBL (nm) VALUES (:name)")
        values = [{'name': nm} for nm in data.getlist('Full_name')]
        conn.execute(stmt, values)
        return data.get('Full_name')


def execute_sql_statement():
    with engine.connect() as conn:
        stmt = text("SELECT * FROM SSC_ATT_TBL order by id desc")
        result = conn.execute(stmt)
        return result.fetchall()


@app.route("/")
def hello_world():
    return render_template('login.html', company_name="SSC")


@app.route("/showvalue", methods=['GET', 'POST'])
def list_jobs():
    if request.method == 'POST':
        data = request.form
        full_name = add_application_to_db(data)
        return render_template('showvalue.html', full_name=full_name)
    else:
        data = execute_sql_statement()
        return render_template("showvalue.html", data=data)


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
