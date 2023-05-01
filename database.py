
from sqlalchemy import create_engine, text

db_connection_string = "mysql+pymysql://ej639yj5aky8mj8owvys:pscale_pw_F6NLqNpERB9ZKm5nWEluf3gmXXKZfaFohIkSpNy2dEN@aws.connect.psdb.cloud/ssc_att?charset=utf8mb4"

engine = create_engine(
  db_connection_string,
  connect_args={
    "ssl":{
      "ssl_ca": "/etc/ssl/cert.pem"
    }
  }
)

with engine.connect() as conn:
  result = conn.execute(text("select nm from SSC_ATT_TBL"))
print(result.all())


