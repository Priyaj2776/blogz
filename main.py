from flask import Flask, request, redirect, render_template,flash,session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:Abcd1234@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    deleted = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.deleted = False
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
 
@app.route('/', methods=['GET'])
def index():
    users =  User.query.all()
    return render_template('index.html',users=users)

    
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        verifypassword = request.form['verifypassword'].strip()
        error = False
        
        #Validate if username and password are not blank
        if(username == ""):
            flash("Username cannot be blank","error")
            error = True
        elif(len(username)<=3):
            flash("Username too short","error")
            error = True
            
        if(password == ""):
            flash("Password cannot be blank","error")
            error = True
        elif len(password)<=3:
            flash("Password too short","error")
            error = True

        if(verifypassword != password):
            flash("Password and verify password dont match","error")
            error = True
        

        if(error == False):
            user = User.query.filter_by(username=username).first()    
            if user:
                flash("Username already exists.","error")
                error = True

        if(error == False):
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/newblog')
        else:
            return render_template('signup.html')
            
    else:
        return render_template('signup.html')

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        
        #Validate if username and password are not blank
        if(username == ""):
            flash("Username cannot be blank","error")
        if(password == ""):
            flash("password cannot be blank","error")
        
        #If username or password are blank redirect user to login page
        if(username =="" or password ==""):
            return render_template('login.html',username = username)
    
        else:
            user = User.query.filter_by(username=username).first()
            if user :
                if user.password == password:
                    session['username'] = username
                    flash("Logged in")
                    return redirect('/newblog')
                else:
                    flash('Invalid Password', 'error')
                    return render_template('login.html',username = username)
            else:
                flash('User does not exist. Please signup.', 'error')
                return redirect('/signup')
    else:
        return render_template('login.html')

@app.route('/logout', methods=['GET'])
def logout():
    del session['username']
    return redirect('/listblogs')

@app.route('/listblogs', methods=['GET'])
def listblogs():
    id = request.args.get('id')
    user = request.args.get('user')
    
    per_page = 5
    page = 1
    try:
        page = int(request.args.get('page'))
    except:
        pass

    blogs = None
    if(id != None): 
        blogs = Blog.query.filter_by(id=int(id)).paginate(page, per_page)
        return render_template('blogs.html',pagetitle = "Build A Blog", 
                                            blogs = blogs) 
    else:      
        if(user != None):
            blogs = Blog.query.filter_by(owner_id = user).paginate(page, per_page)
            return render_template('singleUser.html',pagetitle = "Build A Blog", 
                                            blogs = blogs)
        else:
            #blogs = Blog.query.all().paginate(page=1, per_page=5, error_out=True, max_per_page=None)
            blogs = Blog.query.paginate(page, per_page)
            
            return render_template('blogs.html',pagetitle = "Build A Blog", 
                                            blogs = blogs) 
    
    

@app.route('/newblog', methods=['POST','GET'])
def newblog():
    
    title = ""
    body = ""
    title_error = ""
    body_error = ""

    currentuser = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        
        title = request.form['title']
        body = request.form['body']
        
        if(title.strip() == ""):
            title_error = "Title cannot be blank"
        
        if(body.strip() == ""):
            body_error = "Your blog body cannot be empty"
        
        if(title_error == "" and body_error == ""):
            
            new_blog = Blog(title, body, currentuser)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/listblogs?id=' + str(new_blog.id))

    return render_template('newblog.html',pagetitle = "Add a Blog Entry",
                                        title = title,
                                        title_error = title_error, 
                                        body = body, 
                                        body_error=body_error)

@app.before_request
def require_login():
    allowed_routes = ['listblogs','login', 'signup','index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

    

if __name__ == '__main__':
    app.run()