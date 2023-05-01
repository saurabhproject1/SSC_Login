from flask import Flask, render_template, jsonify, request


app=Flask(__name__)

jobs = [
  {
    'Id': 1,
    'Name_': 'Saurabh'
  }
]

@app.route("/")
def hello_world():
  return render_template('login.html',jobs=jobs,company_name = "SSC")


@app.route("/showvalue", methods = ['post'])
def list_jobs():
  data = request.form
  return jsonify(data)


if __name__ == "__main__":
  app.run(host='0.0.0.0',debug=True)



