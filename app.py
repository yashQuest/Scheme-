from flask import Flask,render_template,request,url_for,flash,redirect
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="yash2622007",
    database="government_schemes"
)

cursor = db.cursor(dictionary=True)

app=Flask(__name__)
app.secret_key="My_secret_key"



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


@app.route("/ContactUs" ,methods=["POST","GET"])
def contact():
    if request.method=="POST":
        name=request.form.get("name")
        email=request.form.get("email")
        subject=request.form.get("subject")
        message=request.form.get("message")

        query="""INSERT INTO contacts(name,email,subject,message)VALUES(%s,%s,%s,%s);"""
        cursor.execute(query,(name,email,subject,message))
        db.commit()
        flash("Your message has been submitted successfully!", "success")
        return redirect(url_for("contact"))

    return render_template("contactUs.html")


@app.route("/AboutUs")
def aboutUs():
    return render_template("AboutUs.html")

if __name__=="__main__":
    app.run(debug=True)