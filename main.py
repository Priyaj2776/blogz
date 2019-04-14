from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:abcd1234@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    deleted = db.Column(db.Boolean)

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.deleted = False


@app.route('/', methods=['GET'])
def index():
    
    return redirect('/blog')


@app.route('/blog', methods=['GET'])
def listBlogs():

    id = request.args.get('id')
    
    if(id != None): 
        blog = Blog.query.get(int(id))
        title = ""
        body = ""

        if(blog == None):
            body = "Invalid blog ID"
        else:
            title = blog.title
            body = blog.body

        return render_template('blog.html',pagetitle = title, 
                                            body = body)
    else:      
        blogs = Blog.query.filter_by(deleted=False).all()
        return render_template('blogs.html',pagetitle = "Build A Blog", 
                                            blogs = blogs)

    

 

@app.route('/newblog', methods=['POST','GET'])
def NewPost():
    
    title = ""
    body = ""
    title_error = ""
    body_error = ""

    if request.method == 'POST':
        
        title = request.form['title']
        body = request.form['body']
        
        if(title.strip() == ""):
            title_error = "Title cannot be blank"
        
        if(body.strip() == ""):
            body_error = "Your blog body cannot be empty"
        
        if(title_error == "" and body_error == ""):
            new_blog = Blog(title, body)
            db.session.add(new_blog)
            db.session.commit()
            return redirect('/blog?id=' + str(new_blog.id))

    return render_template('newblog.html',pagetitle = "Add a Blog Entry",
                                          title = title,
                                          title_error = title_error, 
                                          body = body, 
                                          body_error=body_error)
    
    

if __name__ == '__main__':
    app.run()