from flask import Flask,render_template,request,flash,redirect,url_for
import os
import sqlite3
import pandas as pd


app=Flask(__name__)
app.config['UPLOAD_FOLDER']="static\Excel"
app.secret_key="123"

con=sqlite3.connect("MyData.db")
con.execute("create table if not exists data(pid integer primary key,exceldata TEXT)")
con.close()

@app.route("/",methods=['GET','POST'])
def index():

    con = sqlite3.connect("MyData.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from data")
    data = cur.fetchall()
    con.close()

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

@app.route('/view_excel/<string:id>')
def view_excel(id):
    con = sqlite3.connect("MyData.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from data where pid=?",(id))
    data = cur.fetchall()
    print(data)
    for val in data:
        path = os.path.join("static/Excel/",val[1])
        print(val[1])
        data=pd.read_csv(path)
    con.close()
    return render_template("view_excel.html",data=data.to_html(index=False,classes="table table-bordered").replace('<th>','<th style="text-align:center">'))

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
        con.close()

if __name__ == '__main__':
    app.run(debug=True)