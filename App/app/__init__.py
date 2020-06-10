from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager 
import pymysql

app = Flask(__name__)

#SQLAlchemy duomenu bazes konfiguravimas su MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:areta@158.129.200.236:57306/network-testing-db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = "2016374113"

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.login_view = 'routes.login_user'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

from app.routes import main as main_blueprint
app.register_blueprint(main_blueprint)

from app.models import User
db.create_all()
    
if __name__== '__main__':
    app.run(debug=True)