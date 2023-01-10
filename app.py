from flask import Flask,render_template,request,flash,redirect,url_for,session
from flask_session import Session
import os
import sqlite3
import json
import pandas as pd


app=Flask(__name__)
app.config['UPLOAD_FOLDER']="static\Excel"
app.config["SESSION_PERMANENT"] = False
app.secret_key="123"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

con=sqlite3.connect("MyData.db")
con.execute("create table if not exists data(pid integer primary key,exceldata TEXT)")
con.close()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            session["login_check"] = "yes"
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route("/index",methods=['GET','POST'])
def index():
    if session.get("login_check", "yes"):
        con = sqlite3.connect("MyData.db")
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("select * from data")
        data = cur.fetchall()
        con.close()
        my_var = session.get('my_var', None)
        print(my_var)
        if request.method == 'POST':
            uploadExcel = request.files['uploadExcel']
            if uploadExcel.filename != '':
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], uploadExcel.filename)
                uploadExcel.save(filepath)
                con = sqlite3.connect("MyData.db")
                cur = con.cursor()
                cur.execute("insert into data(exceldata)values(?)", (uploadExcel.filename,))
                con.commit()
                flash("Excel Sheet Upload Successfully", "success")
                con = sqlite3.connect("MyData.db")
                con.row_factory = sqlite3.Row
                cur = con.cursor()
                cur.execute("select * from data")
                data = cur.fetchall()
                con.close()
                return render_template("ExcelUpload.html", data=data)
        return render_template("ExcelUpload.html",data=data)
    return redirect(url_for('login'))

@app.route('/view_excel/<string:id>')
def view_excel(id):
    con = sqlite3.connect("MyData.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from data where pid=?",(id))
    data = cur.fetchall()
    for val in data:
        path = os.path.join("static/Excel/",val[1])
        data=pd.read_excel(path)
        json_data3 = json.dumps(json.loads(data.to_json(orient="records")))
    return render_template("template.html",data=json_data3)
    

@app.route('/delete_record/<string:id>')
def delete_record(id):
    try:
        con=sqlite3.connect("MyData.db")
        cur=con.cursor()
        cur.execute("delete from data where pid=?",[id])
        con.commit()
        flash("Record Deleted Successfully","success")
    except:
        flash("Record Deleted Failed", "danger")
    finally:
        return redirect(url_for("index"))
    

# @app.route('/excel/<string:id>')
# def excel(id):
#     con = sqlite3.connect("MyData.db")
#     con.row_factory = sqlite3.Row
#     cur = con.cursor()
#     cur.execute("select * from data where pid=?",(id))
#     data = cur.fetchall()
#     for val in data:
#         path = os.path.join("static/Excel/",val[1])
#         data=pd.read_excel(path)
#         json_data3 = json.dumps(json.loads(data.to_json(orient="records")))
#     return render_template("view_excel.html",data=json_data3)


if __name__ == '__main__':
    app.run(debug=True)