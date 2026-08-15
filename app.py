from flask import Flask,render_template,request,url_for
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yash2622007",
    database="government_schemes"
)

cursor = db.cursor(dictionary=True)

app=Flask(__name__)



@app.route("/home")
def home():
    return render_template("home.html")




@app.route("/find/<int:scheme_id>")
def find(scheme_id):
    query="SELECT * FROM schemes WHERE category_id=%s"


    cursor.execute(query,(scheme_id,))
    schemes = cursor.fetchall()
    return render_template("test.html",schemes=schemes,num=len(schemes))

@app.route("/Eligibility")
def eligibility():
    return render_template("eligibility.html")


@app.route("/ContactUs")
def contact():
    return render_template("contactUs.html")

if __name__=="__main__":
    app.run(debug=True)