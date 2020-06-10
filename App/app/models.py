from . import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    #scenarios = db.relationship("Scenario", back_populates="user", lazy=True)


class Scenario(db.Model):
    __tablename__ = 'scenario'

    id = db.Column(db.String(36), primary_key=True)        
    #user_id = db.Column(db.String, db.ForeignKey('user.id'), nullable=False)
    #user = db.relationship("User", back_populates="scenarios")  # Nurodau rysi su "parent"
    tests = db.relationship("ScenarioTest", back_populates="scenario", lazy=True)   # Nurodau rysi su "child"


class ScenarioTest(db.Model):
    __tablename__ = 'scenariotest'

    id = db.Column(db.String(36), primary_key=True)  
    date = db.Column(db.DateTime, nullable=False)
    source = db.Column(db.String(16), nullable=False)
    destination = db.Column(db.String(16), nullable=False)
    program = db.Column(db.String(6), nullable=False)
    duration = db.Column(db.String(40), nullable=True)
    protocol = db.Column(db.String(40), nullable=True)
    num_streams = db.Column(db.String(40), nullable=True)
    throughput = db.Column(db.String(40), nullable=True)  # bits_per_second
    mss = db.Column(db.String(40), nullable=True)
    tos = db.Column(db.String(40), nullable=True)
    scenario_id = db.Column(db.String(36), db.ForeignKey('scenario.id'), nullable=False)
    scenario = db.relationship("Scenario", back_populates="tests", lazy=True)  # Nurodau rysi su "parent"
    #results = db.relationship("Results", back_populates="test", lazy=True)   # Nurodau rysi su "child"


class Results(db.Model):
    __tablename__ = 'results'

    scenario_id = db.Column(db.String(36), primary_key=True)
    id = db.Column(db.String(36), nullable=False) 
    date = db.Column(db.DateTime, nullable=False) # TCP pralaidumas
    program = db.Column(db.String(40), nullable=False)  
    source = db.Column(db.String(40), nullable=True) 
    destination = db.Column(db.String(40), nullable=True)  
    protocol = db.Column(db.String(40), nullable=True) 
    duration = db.Column(db.String(40), nullable=True)  
    num_streams = db.Column(db.String(40), nullable=True) 
    throughput = db.Column(db.String(40), nullable=True)  
    mss = db.Column(db.String(40), nullable=True) 
    tos = db.Column(db.String(40), nullable=True)
    
    #test = db.relationship("ScenarioTest", back_populates="results", lazy=True)
    #test_id = db.Column(db.String(36), db.ForeignKey('scenariotest.id'))     
    bits_per_second = db.Column(db.String(40), nullable=True) # TCP pralaidumas
    lost_percent = db.Column(db.String(40), nullable=True)  
    jitter_ms = db.Column(db.String(40), nullable=True) 


 