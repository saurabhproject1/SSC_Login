
from sqlalchemy import create_engine, text

db_connection_string = "mysql+pymysql://9q5hmn3z07sg04w2hnbo:pscale_pw_DyoLxwHaohN2Sc1Kb3xW6S8uMP749buFS0sHjFlDjGF@aws.connect.psdb.cloud/ssc_att?charset=utf8mb4"

engine = create_engine(
  db_connection_string,
  connect_args={
    "ssl":{
      "ssl_ca": "/etc/ssl/cert.pem"
    }
  }
)


def add_application_to_db(data):
    with engine.connect() as conn:
        stmt = text("INSERT INTO SSC_ATT_TBL (nm) VALUES (:name)")
        values = [{'name': nm} for nm in data.getlist('Full_name')]
        conn.execute(stmt, values)
        return data.get('Full_name')

