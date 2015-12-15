from flask import Flask, render_template, request, session, url_for, redirect
import shelve, hashlib, os

app = Flask(__name__)
app.secret_key = os.urandom(24)

IMG_DIR = './static/i/'
PASS_LOCATION = 0
IMG_LIST = 1
USERS = shelve.open("USERS", writeback = True)

def authenticate( user, passw ):
	passw = hashlib.sha256(passw).hexdigest()
	return USERS[user][PASS_LOCATION] == passw

def validUser( user ):
	return user in USERS

def register(user, password):
	password = hashlib.sha256(password).hexdigest()
	USERS[user] = [ password, [] ]
	if not os.path.exists( IMG_DIR + user ):
			os.mkdir( IMG_DIR + user )

@app.route("/follow", methods =["POST"])
def follow():
	if 'user' in session:
		user = session['user']
		return str(request.form.getlist('following'))
	else:
		return render_template("index.html")

@app.route("/users")
def users():
		if 'user' in session:
			user = session['user']
			all_users = {}
			for u in USERS.keys():
					all_users[u] = USERS[u][IMG_LIST][-1]
			return render_template( "users.html", USER= user, USERS= all_users)
		else:
			return render_template( "index.html" )

@app.route("/public/<NAME>")
def public( NAME ):
	NAME = str(NAME)
	if 'user' in session:
		user = session['user']

		if validUser(NAME):
			return render_template( "public.html", USER = user, USER2 = NAME, PHOTOS = USERS[NAME][IMG_LIST])
		else:
			return render_template( "404.html", USER = user, USER2 = NAME)
	else:
		return render_template( "index.html" )

@app.route("/upload")
def upload():
	return render_template("upload.html", USER= session['user'])

@app.route("/")
@app.route("/home")
def home():
	if 'user' in session:
		user = session['user']
		return render_template( "home.html", USER = user, PHOTOS = USERS[user][IMG_LIST] )
	else:
		return render_template( "index.html" )

@app.route("/sendpic", methods=["POST"])
def sendpic():
	if 'user' in session:
		f = request.files['picture']
		user = session['user']
		saveName = IMG_DIR + user + '/' + f.filename
		if os.path.exists( IMG_DIR + user ):
			f.save( saveName )
			USERS[user][IMG_LIST].append(f.filename)
		return redirect( url_for("home") )
	else:
		return render_template( "index.html" )

@app.route("/logout")
def logout():
	if 'user' in session:
		session.pop('user')
		return redirect( url_for("home") )
	else:
		return render_template( "index.html" )

@app.route("/login", methods=["POST"] )
def login():
	u = str(request.form['usernameo'])
	p = str(request.form['passw'])

	if 'login' in request.form:
		if validUser(u):
				if authenticate( u, p ):
					session["user"] = u
					return redirect( url_for("home") )
				else:
					return render_template( "index.html", MESSAGE2 = "Password Incorrect")
		else:
					return render_template( "index.html", MESSAGE2 = "Username Incorrect")
	elif 'register' in request.form:

		if validUser(u):
			return render_template("index.html", MESSAGE2 = "Username already taken")
		else:
				register(u, p)
				return render_template("index.html", MESSAGE1 = "User registered, please login")



if __name__ == "__main__":
	app.debug = True
	app.run()
