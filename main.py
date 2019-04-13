from flask import Flask
from flask_sqlalchemy import SQLAlchemy 

app = Flask('__name__')

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:abcd1234@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Task(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(120))

    def __init__(self, name):
        self.name = name

if __name__ == '__main__':
    app.run()
