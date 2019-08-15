from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Database_setup import Users, Base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.pool import StaticPool
import os

app = Flask(__name__)
engine = create_engine("sqlite:///storeitemes.db", connect_args={'check_same_thread': False},
                    poolclass=StaticPool)
appRoot = os.path.dirname(os.path.abspath(__file__))
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
sessionDB = DBSession()


@app.route("/")
def home():
    students = sessionDB.query(Users).order_by(Users.score.desc()).all()
    return render_template("home.html", students=students)


@app.route("/newStudent", methods=["GET", "POST"])
def new_student():
    try:
        if request.method == "POST":
            if request.files.get('pic'):
                target = os.path.join(appRoot, "static/img/st/")
                file = request.files["pic"]
                # get file extension
                ext = file.filename[file.filename.rfind("."):].lower()
                filename = str(request.form["name"]) + ext
                destination = "/".join([target, filename])
                new_student = Users(name=request.form["name"], score=request.form["score"], ext=ext)
            else:
                new_student = Users(name=request.form["name"], score=request.form["score"])
            sessionDB.add(new_student)
            sessionDB.commit()
            if request.files.get('pic'):
                file.save(destination)
            return redirect(url_for("home"))
        else:
            return render_template("newStudent.html")
    except IntegrityError:
        sessionDB.rollback()
        flash("Student is already existed")
        return redirect(url_for("new_student"))

@app.route("/searchStudent/", methods=["GET", "POST"])
def searchstudent():
    if request.method == "POST":
        if request.form["searchName"]:
            students = sessionDB.query(Users).filter(Users.name.like("%{}%".format(request.form["searchName"]))).all()
        else:
            return render_template("searchstudent.html")
        return render_template("searchstudent.html", students=students)
    else:
        return render_template("searchstudent.html")

@app.route("/new_image/<string:student_id>", methods=["GET","POST"])
def new_image(student_id):
    editedStudent = sessionDB.query(Users).filter_by(id=student_id).one()
    if request.method == "POST":
        if request.files.get('pic'):
            target = os.path.join(appRoot, "static/img/st/")
            file = request.files["pic"]
            # get file extension
            ext = file.filename[file.filename.rfind("."):].lower()
            filename = str(editedStudent.name) + ext
            destination = "/".join([target, filename])
            editedStudent.ext=ext
        sessionDB.add(editedStudent)
        sessionDB.commit()
        if request.files.get('pic'):
            file.save(destination)
        return redirect(url_for("home"))
    else:
        return render_template("new_image.html", student=editedStudent)

@app.route("/student/<int:user_id>/addscore", methods=["GET","POST"])
def addscore(user_id):
    editedUser = sessionDB.query(Users).filter_by(id=user_id).one()
    if request.method == "POST":
        if request.form["score"]:
            editedUser.score += int(request.form["score"])
        sessionDB.add(editedUser)
        sessionDB.commit()
        return redirect(url_for("searchstudent"))

@app.route("/StDel/<string:user_id>", methods=["GET","POST"])
def StDel(user_id):
    student = sessionDB.query(Users).filter_by(id=user_id).one()
    if student.ext != "xzy":
        target = os.path.join(appRoot, "static/img/st/", student.name+student.ext)
        os.remove(target)
    sessionDB.delete(student)
    sessionDB.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.secret_key = "Su9er#P@ssw0rd"
    app.run(debug=True, port=81)
