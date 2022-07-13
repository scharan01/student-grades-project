'''from asyncio.windows_events import NULL
from operator import truediv
from pickle import TRUE
from sre_constants import SUCCESS'''
from flask import Flask, render_template, flash, redirect, url_for, request, session, logging
from flask_mysqldb import MySQL
from wtforms import Form, StringField, SelectMultipleField,TextAreaField, PasswordField,validators, RadioField, SelectField, IntegerField,BooleanField
from wtforms.validators import InputRequired
from passlib.hash import sha256_crypt
from functools import wraps
from flask_ngrok import run_with_ngrok


app = Flask(__name__)


#run_with_ngrok(app)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Satya_2001'
app.config['MYSQL_DB'] = 'students'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
app.secret_key = 'random'

values = []

class StudentSignupForm(Form):
	fullname = StringField('Full Name', [validators.InputRequired(),validators.Length(min = 1, max = 40)])
	roll = StringField('Roll Number', [validators.InputRequired(), validators.NoneOf(values = values, message = "Account already exists,please login")])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message = 'Passwords aren\'t matching enter again!')
	])
	confirm = PasswordField('Confirm Password',[validators.InputRequired()])
	batch = SelectField('Batch', choices=['2023', '2024', '2025', '2026'])
	branch = SelectField('Branch', choices=['CSE', 'ECE', 'EEE', 'CHEM','CIV','MECH','BMS','MAT','PHY','CHEM','BIO'])
	email = StringField('SNU Email ID', [validators.InputRequired(),validators.Length(min = 1, max = 40)])
	mobile = StringField('Mobile', [validators.InputRequired(),validators.Length(min = 10, max = 12)])

class InstructorSignupForm(Form):
	fullname = StringField('Full Name', [validators.Length(min = 1, max = 40)])
	insid = StringField('Instructor ID', [validators.InputRequired(), validators.NoneOf(values = values, message = "Account already exists,please login")])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message = 'Passwords aren\'t matching enter again!')
	])
	confirm = PasswordField('Confirm Password')
	title = SelectField('Title', choices=['Associate Professor', 'Assistant Professor', 'Teaching Assistant', 'Junior Professor'],
                       validators=[InputRequired()])
	branch = SelectField('Branch', choices=['CSE', 'ECE', 'EEE', 'CHEM','CIV','MECH','BMS','MAT','PHY','CHEM','BIO'],
                       validators=[InputRequired()])
	email = StringField('SNU Email ID', [validators.Length(min = 1, max = 40)])
	mobile = StringField('Mobile', [validators.Length(min = 10, max = 12)])

class LoginForm(Form) :
	roll =  StringField('Roll Number', [validators.InputRequired(),validators.Length(min = 10, max = 20)])
	password =  PasswordField('Password', [validators.InputRequired()])

class InstructorLoginForm(Form) :
	insid =  StringField('Instructor ID', [validators.InputRequired(),validators.Length(min = 10, max = 20)])
	password =  PasswordField('Password', [validators.InputRequired()])

class AddStudentsForm(Form):
	roll = StringField('Roll Number', [validators.InputRequired(), validators.NoneOf(values = values, message = "Student already added!")])

class AddExamForm(Form) :
	name = StringField('Name of the Exam',[validators.InputRequired(),validators.Length(min = 1, max = 20)])
	maxmarks = IntegerField('Maximum Marks',[validators.InputRequired(),validators.NumberRange(min=1)])
	weightage = IntegerField('Weightage',[validators.InputRequired(),validators.NumberRange(min=1,max=100)])

class AddCourseForm(Form) :
	coursecode = StringField('Course Code', [validators.InputRequired(), validators.NoneOf(values = values, message = "Course Code already exists,please use different code")])
	branch = SelectField('Branch', choices=['CSE', 'ECE', 'EEE', 'CHEM','CIV','MECH','BMS','MAT','PHY','CHEM','BIO'],
                       validators=[InputRequired()])
	batch = SelectField('batch', choices=['2023', '2024', '2025', '2026'],
                       validators=[InputRequired()])
	title = StringField('Course Title',[validators.InputRequired(),validators.Length(min = 1, max = 40)])
	semester = SelectField('Semester', choices=['Monsoon 2022', 'Spring 2021', 'Monsoon 2020'],
                       validators=[InputRequired()])

class ModifyCourseForm(Form) :
	branch = SelectField('Branch', choices=['CSE', 'ECE', 'EEE', 'CHEM','CIV','MECH','BMS','MAT','PHY','CHEM','BIO'],
                       validators=[InputRequired()])
	batch = SelectField('Semester', choices=['2023', '2024', '2025', '2026'],
                       validators=[InputRequired()])
	title = StringField('Course Title',[validators.InputRequired(),validators.Length(min = 1, max = 40)])
	semester = SelectField('Semester', choices=['Monsoon 2022', 'Spring 2021', 'Monsoon 2020'],
                       validators=[InputRequired()])

class ModifyExamForm(Form) :
	maxmarks = IntegerField('Maximum Marks',[validators.InputRequired(),validators.NumberRange(min=1)])
	weightage = IntegerField('Weightage',[validators.InputRequired(),validators.NumberRange(min=1,max=100)])


@app.route('/', methods = ['GET', 'POST'])
def login():
	
	form = LoginForm(request.form)

	if request.method == 'POST' and form.validate():
		rollnumber = form.roll.data
		password_candidate = form.password.data

		cur = mysql.connection.cursor()

		result = cur.execute('SELECT * FROM student_signup WHERE Roll_Number = %s', [rollnumber])
		print(result)

		if result>0:
			data = cur.fetchone()
			password = data['Student_password']

			if sha256_crypt.verify(password_candidate, password):
				session['rollnumber'] = rollnumber
				return redirect(url_for('studentdash'))
			else:
				error = 'Wrong Password Try Again!'
				return render_template('layout.html', form=form,error = error)
		    
          #cur.close();
        
		else :
			error = 'You dont have an account please create using the link given below'
			return render_template('layout.html', form=form,error = error)
	
	return render_template('layout.html',form=form)

@app.route('/instructorlogin', methods = ['GET', 'POST'])
def instructorlogin():
	form = InstructorLoginForm(request.form)

	if request.method == 'POST' and form.validate():
		insid = form.insid.data
		password_candidate = form.password.data

		cur = mysql.connection.cursor()

		result = cur.execute('SELECT * FROM instructor_signup WHERE instructor_ID = %s', [insid])
		
        
		if result>0:
			data = cur.fetchone()
			password = data['instructor_password']

			if sha256_crypt.verify(password_candidate, password):
				session['insid'] = insid
				
				return redirect(url_for('instructordash'))
			else:
				error = 'Wrong Password Try Again!'
				return render_template('instructorlogin.html',form=form, error = error)

		else :
			error = 'You dont have an account please create using the link given below'
			return render_template('instructorlogin.html', form=form,error = error)
	
	return render_template('instructorlogin.html',form=form)

@app.route('/signup', methods = ['GET', 'POST'])
def signup():

	values.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT Roll_Number FROM student_signup")
	b = cur.fetchall()
	for i in range(q):
		values.append(b[i]['Roll_Number'])
	cur.close()
	
	form = StudentSignupForm(request.form)
	
	if request.method == 'POST' and form.validate() :
		
		fullname = form.fullname.data
		roll = form.roll.data
		password = sha256_crypt.encrypt(str(form.password.data))
		batch = form.batch.data
		branch = form.branch.data
		email = form.email.data
		phone = form.mobile.data
		
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO student_signup VALUES(%s, %s, %s, %s, %s, %s, %s)", (roll, fullname, branch, email, phone,batch,password))
		mysql.connection.commit()
		cur.close()
		return redirect(url_for('login'))
	return render_template('signup.html',form=form)

@app.route('/instructorsignup', methods = ['GET', 'POST'])
def instructorsignup():
	values.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT instructor_ID FROM instructor_signup")
	b = cur.fetchall()
	for i in range(q):
		values.append(b[i]['instructor_ID'])
	cur.close()
	
	form = InstructorSignupForm(request.form)
	
	if request.method == 'POST' and form.validate() :
		
		print('hello')
		fullname = form.fullname.data
		insid = form.insid.data
		password = sha256_crypt.encrypt(str(form.password.data))
		title = form.title.data
		branch = form.branch.data
		email = form.email.data
		phone = form.mobile.data
		cur = mysql.connection.cursor()
		cur.execute("INSERT INTO instructor_signup VALUES(%s, %s, %s, %s, %s, %s, %s)", (insid, fullname, phone, branch,password,title,email))
		mysql.connection.commit()
		cur.close()
		return redirect(url_for('instructorlogin'))
	return render_template('instructorsignup.html',form=form)


@app.route('/addcourse', methods = ['GET', 'POST'])

def addcourse():

	values.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT course_code FROM courses_list")
	b = cur.fetchall()
	for i in range(q):
		values.append(b[i]['course_code'])
	cur.close()

	form = AddCourseForm(request.form)

	if session.get('insid',None) is not None :
		if request.method == 'POST' and form.validate() :
			coursecode = form.coursecode.data
			insid = session['insid']
			branch = form.branch.data
			batch = form.batch.data
			title = form.title.data
			semester = form.semester.data
			cur = mysql.connection.cursor()
			cur.execute("INSERT INTO courses_list VALUES(%s, %s, %s, %s, %s, %s)", (coursecode, insid, branch, batch,title,semester))
			mysql.connection.commit()
			cur.close()
			return redirect(url_for('instructordash'))
		return  render_template('addcourse.html',form=form)
	return redirect(url_for('instructorlogin'))

@app.route('/instructordash')
def instructordash():
	
	if session.get('insid',None) is not None :
		insid = session['insid']
		cur = mysql.connection.cursor()
		cur.execute("SELECT * FROM courses_list WHERE instructor_ID = %s",(insid,))
		details = cur.fetchall()
		cur.close()
		return render_template("instructordash.html",details=details)
	return redirect(url_for('instructorlogin'))

@app.route('/coursedetails/<string:coursename>')
def coursedetails(coursename):
	if session.get('insid',None) is not None :
		cur = mysql.connection.cursor()
		cur.execute("SELECT exam_details.exam_maxmarks,exam_marks.exam_name FROM exam_marks INNER JOIN exam_details ON exam_details.exam_name = exam_marks.exam_name WHERE exam_marks.course_code = %s GROUP BY exam_marks.exam_name",(coursename,))
		exams = cur.fetchall()
		cur.execute("SELECT exam_details.exam_maxmarks,student_signup.student_name,exam_marks.exam_name,exam_marks.student_marks,exam_marks.student_roll FROM exam_marks LEFT JOIN student_signup ON student_signup.roll_number = exam_marks.student_roll JOIN exam_details ON exam_details.exam_name = exam_marks.exam_name WHERE exam_marks.course_code = %s and exam_details.course_code = %s ORDER BY exam_marks.student_roll",(coursename,coursename))
		marks = cur.fetchall()
		cur.execute("SELECT * FROM courses_list WHERE course_code = %s",(coursename,))
		details = cur.fetchall()
		cur.execute("SELECT student_courses.Roll_Number,student_signup.Student_Name,student_signup.Student_email,student_signup.Student_phone FROM student_courses LEFT JOIN student_signup ON student_courses.Roll_Number = student_signup.Roll_Number WHERE student_courses.course_code = %s ORDER BY student_courses.roll_number",(coursename,))
		students = cur.fetchall()
		
		cur.close()
		return render_template("coursedetails.html",students=students,details=details,marks=marks,exams=exams,coursename = coursename)
	return redirect(url_for('instructorlogin'))


@app.route('/addstudents/<string:coursename>', methods = ['GET', 'POST'])
def addstudents(coursename):

	values.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT Roll_Number FROM student_courses WHERE Course_code = %s",(coursename,))
	b = cur.fetchall()
	for i in range(q):
		values.append(b[i]['Roll_Number'])
	cur.close()
	
	form = AddStudentsForm(request.form)

	if session.get('insid',None) is not None :
		
		if request.method == 'POST' :
			
			checkbox = request.form.getlist('checkbox')
			s = ""
			for check in checkbox :
				if check in values :
					s += check + ","
					continue
				cur = mysql.connection.cursor()
				cur.execute("INSERT INTO student_courses VALUES(%s,%s)",(check,coursename))
				mysql.connection.commit()
				cur.execute("INSERT INTO exam_marks(student_roll,exam_name,course_code) (SELECT DISTINCT %s,exam_name,%s  FROM exam_marks WHERE course_code = %s)",(check,coursename,coursename))
				mysql.connection.commit()
			if s != "" :
				s += " is/are not added as they are already added in the course"
				flash(s,'danger')
			else :
				flash("Students added successfully!",'success')

		cur = mysql.connection.cursor()	
		cur.execute("SELECT student_signup.Roll_Number,student_signup.Student_Name FROM student_signup INNER JOIN courses_list ON courses_list.batch = student_signup.batch AND courses_list.branch = student_signup.Student_branch WHERE courses_list.course_code = %s",(coursename,))
		details = cur.fetchall()
		cur.close()
		return render_template("addstudents.html",form=form,details=details,coursename = coursename)
	return redirect(url_for('instructorlogin'))
	
@app.route('/addstudentsm/<string:coursename>', methods = ['GET', 'POST'])
def addstudentsm(coursename):

	values.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT Roll_Number FROM student_courses WHERE Course_code = %s",(coursename,))
	b = cur.fetchall()
	for i in range(q):
		values.append(b[i]['Roll_Number'])
	cur.close()
	
	form = AddStudentsForm(request.form)

	if session.get('insid',None) is not None :
		
		if request.method == 'POST' and form.validate():
			rollno = form.roll.data
			cur = mysql.connection.cursor()
			cur.execute("INSERT INTO student_courses VALUES(%s,%s)",(rollno,coursename))
			mysql.connection.commit()
			cur.execute("INSERT INTO exam_marks(student_roll,exam_name,course_code) (SELECT DISTINCT %s,exam_name,%s  FROM exam_marks WHERE course_code = %s)",(rollno,coursename,coursename))
			mysql.connection.commit()
			flash('Student added successfully','success')
		
		else:
			flash('Student already exists!','danger')

		cur = mysql.connection.cursor()	
		cur.execute("SELECT student_signup.Roll_Number,student_signup.Student_Name FROM student_signup INNER JOIN courses_list ON courses_list.batch = student_signup.batch AND courses_list.branch = student_signup.Student_branch WHERE courses_list.course_code = %s",(coursename,))
		details = cur.fetchall()
		cur.close()
		return redirect(url_for('addstudents',coursename=coursename))
	return redirect(url_for('instructorlogin'))

@app.route('/addexam/<string:coursename>', methods = ['GET', 'POST'])
def addexam(coursename):

	form = AddExamForm(request.form)
	values.clear()
	cur = mysql.connection.cursor()
	q = cur.execute("SELECT exam_name FROM exam_details WHERE course_code = %s",(coursename,))
	b = cur.fetchall()
	for i in range(q):
		values.append(b[i]['exam_name'])
	cur.close()

	if session.get('insid',None) is not None :
		
		if request.method == 'POST' and form.validate() :
			
			marks = request.form.getlist('Marks')
			roll = request.form.getlist('roll')
			examname = form.name.data
			maxmarks = form.maxmarks.data
			weightage = form.weightage.data
			index = 0

			if examname in values :
				flash("An exam with the same name already exists!",'danger')
				return redirect(url_for('addexam',coursename=coursename))

			for mark in marks :
				if mark == '' :
					flash("student marks cannot be empty!",'danger')
					return redirect(url_for('addexam',coursename=coursename))

			for mark in marks :
				cur = mysql.connection.cursor()
				cur.execute("INSERT INTO exam_marks VALUES(%s,%s,%s,%s)",(coursename,examname,roll[index],mark))
				mysql.connection.commit()
				index += 1
		
			cur = mysql.connection.cursor()
			cur.execute("INSERT INTO exam_details VALUES (%s,%s,%s,%s)",(coursename,examname,maxmarks,weightage))
			mysql.connection.commit()
			cur.close()
			return redirect(url_for('coursedetails',coursename=coursename))
		
		cur = mysql.connection.cursor()	
		cur.execute("SELECT student_courses.Roll_Number,student_signup.Student_Name FROM student_courses LEFT JOIN student_signup ON student_signup.Roll_Number = student_courses.Roll_Number WHERE student_courses.Course_code = %s",(coursename,))
		details = cur.fetchall()
		cur.close()
		return render_template("addexam.html",form=form,details=details,coursename = coursename)
	return redirect(url_for('instructorlogin'))

@app.route('/modifycourse/<string:coursename>', methods = ['GET', 'POST'])

def modifycourse(coursename):

	form = ModifyCourseForm(request.form)

	if session.get('insid',None) is not None :
		if request.method == 'POST'and form.validate():
			branch = form.branch.data
			batch = form.batch.data
			title = form.title.data
			semester = form.semester.data
			cur = mysql.connection.cursor()
			cur.execute("UPDATE courses_list SET branch = %s,batch = %s,course_title = %s,semester = %s WHERE course_code = %s",(branch,batch,title,semester,coursename))
			mysql.connection.commit()
			cur.close()
			
			return redirect(url_for('instructordash'))
		return render_template("modifycourse.html",form=form,coursename=coursename)
	return redirect(url_for('instructorlogin'))

@app.route('/instructorlogout')
def instructorlogout():
	session.pop('insid',None)
	return redirect(url_for('instructorlogin'))

@app.route('/studentdash')
def studentdash():
	
	if session.get('rollnumber',None) is not None :
		rollnumber = session['rollnumber']
		cur = mysql.connection.cursor()
		cur.execute("SELECT instructor_signup.instructor_name,student_courses.Course_code,courses_list.course_title,courses_list.semester FROM student_courses INNER JOIN courses_list ON student_courses.Course_code = courses_list.course_code INNER JOIN instructor_signup ON instructor_signup.instructor_ID = courses_list.instructor_ID WHERE Roll_Number = %s",(rollnumber,))
		details = cur.fetchall()
		cur.close()
		return render_template("studentdash.html",details=details)
	return redirect(url_for('login'))


@app.route('/studentcoursedetails/<string:coursename>')
def studentcoursedetails(coursename):
	if session.get('rollnumber',None) is not None :
		rollnumber = session['rollnumber']
		cur = mysql.connection.cursor()
		cur.execute("SELECT exam_details.exam_maxmarks,exam_details.exam_weightage,exam_marks.exam_name,exam_marks.student_marks FROM exam_marks INNER JOIN exam_details ON exam_details.course_code = exam_marks.course_code AND exam_details.exam_name = exam_marks.exam_name WHERE exam_marks.student_roll = %s and exam_marks.course_code = %s",(rollnumber,coursename))
		marks = cur.fetchall()
		stot,tot,wtot,wtotw = 0,0,0,0
		for mark in marks :
			stot += mark['student_marks']
			tot += mark['exam_maxmarks']
			wtot += (mark['student_marks'] / mark['exam_maxmarks'])*mark['exam_weightage']
			wtotw += mark['exam_weightage']

		tots = { "total_score" : stot , "total_total" : tot , "weighted_score" : round(wtot,2) , "weighted_total" : wtotw }
		cur.close()
		return render_template("studentcoursedetails.html",tots=tots,marks=marks,coursename = coursename)
	return redirect(url_for('login'))

@app.route('/deletecourse/<string:coursename>')
def deletecourse(coursename):
	
	if session.get('insid',None) is not None :
		cur = mysql.connection.cursor()
		cur.execute("DELETE FROM courses_list WHERE course_code = %s",(coursename,))
		mysql.connection.commit()
		cur.close()
		return redirect(url_for('instructordash'))
	return redirect(url_for('instructorlogin'))

@app.route('/deleteexam')
def deleteexam():
	
	if session.get('insid',None) is not None :
		coursename = request.args.get('coursename')
		exam = request.args.get('exam')
		cur = mysql.connection.cursor()
		cur.execute("DELETE FROM exam_details WHERE exam_name = %s and course_code = %s",(exam,coursename))
		mysql.connection.commit()
		cur.execute("DELETE FROM exam_marks WHERE exam_name = %s and course_code = %s",(exam,coursename))
		mysql.connection.commit()
		cur.close()
		return redirect(url_for('coursedetails',coursename=coursename))
	return redirect(url_for('instructorlogin'))

@app.route('/modifyexam', methods = ['GET', 'POST'])
def modifyexam():
	
	form = ModifyExamForm(request.form)

	if session.get('insid',None) is not None :

		coursename = request.args.get('coursename')
		exam = request.args.get('exam')

		if request.method == 'POST' and form.validate() : 
			marks = request.form.getlist('Marks')
			roll = request.form.getlist('roll')
			maxmarks = form.maxmarks.data
			weightage = form.weightage.data
			index = 0

			for mark in marks :
				if mark == '' :
					flash("student marks cannot be empty!",'danger')
					return redirect(url_for('addexam',coursename=coursename))
					
			cur = mysql.connection.cursor()
			for mark in marks :
				
				cur.execute("UPDATE exam_marks SET student_marks = %s WHERE course_code = %s AND exam_name = %s AND student_roll = %s",(mark,coursename,exam,roll[index]))
				mysql.connection.commit()
				index += 1
		
			cur.execute("UPDATE exam_details SET exam_maxmarks = %s,exam_weightage = %s WHERE course_code = %s AND exam_name = %s",(maxmarks,weightage,coursename,exam))
			mysql.connection.commit()
			cur.close()
			return redirect(url_for('coursedetails',coursename=coursename))

		cur = mysql.connection.cursor()
		cur.execute("SELECT student_courses.Roll_Number,student_signup.Student_Name FROM student_courses LEFT JOIN student_signup ON student_signup.Roll_Number = student_courses.Roll_Number WHERE student_courses.Course_code = %s",(coursename,))
		details = cur.fetchall()
		cur.close()
		return render_template('modifyexam.html',exam=exam,coursename=coursename,form=form,details=details)
	return redirect(url_for('instructorlogin'))

@app.route('/updatemark',methods = ['GET', 'POST'])
def updatemark():
	
	if session.get('insid',None) is not None :

		coursename = request.args.get('coursename')
		exam = request.args.get('exam')
		rollnumber = request.args.get('rollnumber')
		marks = request.form['marks']

		if marks == '' :
			flash("student marks cannot be empty!",'danger')
		else :	
			cur = mysql.connection.cursor()
			cur.execute("UPDATE exam_marks SET student_marks = %s WHERE student_roll = %s AND exam_name = %s and course_code = %s",(marks,rollnumber,exam,coursename))
			mysql.connection.commit()
			cur.close()
		return redirect(url_for('coursedetails',coursename=coursename))
	return redirect(url_for('instructorlogin'))

@app.route('/updatemarks', methods = ['GET', 'POST'])
def updatemarks():

	if session.get('insid',None) is not None :

		coursename = request.args.get('coursename')
		exam = request.args.get('exam')

		if request.method == 'POST' : 
			marks = request.form.getlist('Marks')
			roll = request.form.getlist('roll')
			index = 0
					
			cur = mysql.connection.cursor()
			for mark in marks :
				
				if mark != '' :
					cur.execute("UPDATE exam_marks SET student_marks = %s WHERE course_code = %s AND exam_name = %s AND student_roll = %s",(mark,coursename,exam,roll[index]))
					mysql.connection.commit()
				index += 1
		
			cur.close()
			return redirect(url_for('coursedetails',coursename=coursename))

		cur = mysql.connection.cursor()
		cur.execute("SELECT exam_details.exam_maxmarks,student_signup.student_name,exam_marks.student_marks,exam_marks.student_roll FROM exam_marks LEFT JOIN student_signup ON student_signup.roll_number = exam_marks.student_roll  JOIN exam_details ON exam_details.exam_name = exam_marks.exam_name WHERE exam_marks.exam_name = %s AND exam_marks.course_code = %s and exam_details.course_code = %s ORDER BY exam_marks.student_roll;",(exam,coursename,coursename))
		details = cur.fetchall()
		cur.close()
		return render_template('updatemarks.html',exam=exam,coursename=coursename,details=details)
	return redirect(url_for('instructorlogin'))

@app.route('/removestudent')
def removestudent():
	
	if session.get('insid',None) is not None :
		coursename = request.args.get('coursename')
		roll_number = request.args.get('roll_number')
		cur = mysql.connection.cursor()
		cur.execute("DELETE FROM student_courses WHERE course_code = %s AND roll_number = %s",(coursename,roll_number))
		mysql.connection.commit()
		cur.execute("DELETE FROM exam_marks WHERE course_code = %s AND student_roll = %s",(coursename,roll_number))
		mysql.connection.commit()
		cur.close()
		return redirect(url_for('coursedetails',coursename=coursename))
	return redirect(url_for('instructorlogin'))

@app.route('/instructorprofile/<insid>')
def instructorprofile(insid):
	
	if session.get('insid',None) is not None :
		cur = mysql.connection.cursor()
		cur.execute("SELECT * FROM instructor_signup WHERE instructor_ID = %s",(insid,))
		details = cur.fetchall()
		cur.close()
		return render_template('instructorprofile.html',details=details)
	return redirect(url_for('instructorlogin'))

@app.route('/studentprofile/<rollnumber>')
def studentprofile(rollnumber):
	
	if session.get('rollnumber',None) is not None :
		cur = mysql.connection.cursor()
		cur.execute("SELECT * FROM student_signup WHERE roll_number = %s",(rollnumber,))
		details = cur.fetchall()
		cur.close()
		return render_template('studentprofile.html',details=details)
	return redirect(url_for('login'))


@app.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('login'))

if __name__ == '__main__' :
	app.run()