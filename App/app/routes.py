from flask import Blueprint, render_template, request, redirect, flash, url_for, json, jsonify, session
from . import db
from app.models import User, Scenario, ScenarioTest, Results
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import paho.mqtt.publish as publish
import uuid

#===============================================
#===============================================

import paho.mqtt.client as mqtt  
import iperf3

#Laiko ir datos bibliotekos
import datetime 
from datetime import date
import time
from time import ctime
import dateutil.parser 

import subprocess
import sys

import threading
import random

# ------------------- PIRMINIAI DUOMENYS -----------------

port = 1883
broker_address = "158.129.200.236" 
UUID = "7c925d9c-b331-4854-aacb-47c9aa9weweb"  

client = mqtt.Client(UUID)

# --------------------------------------------------------

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Prisijungta sekmingai, grazinamas kodas =", rc)
    else:
        print("Nepavyko prisijungti, grazinamas kodas =", rc)


def on_message(client, userdata, message):
    print("Gauta zinute " + str(message.payload.decode("utf-8")))


def on_message_print(client, userdata, message):
    print("%s %s" % (message.topic, message.payload.decode("utf-8")))


def on_publish(client, userdata, mid):  
    print("Duomenys paskelbti su pranesimo id = ", mid)


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Netiketas atsijungimas")
    else:
        print("Klientas atsijunge sekmingai")


def main ():
    # Konfiguruojam MQTT
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_message_print = on_message_print
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect

    # Jungiames prie brokerio
    client.connect(broker_address, port)  
          
    client.loop_forever()
    print ('Pabaiga')

#========================================================
#========================================================

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/index')
def index():
    return render_template('index.html')


@main.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


@main.route('/home', methods=['GET'])  #I si puslapi ileidzia tik prisijungus, vaikstant tarp puslapiu i ji grizti nebegali
@login_required  
def home():
    return render_template('home.html')


@main.route('/home1', methods=['GET'])
def home1():
    return render_template('home1.html')


@main.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


@main.route('/login', methods=['GET'])
def login():
    return render_template('index.html', login=str(login))


@main.route('/testing', methods=['GET'])
def testing():
    #user_id = current_user.get_id()
    all_data = ScenarioTest.query.all()
    return render_template('testing.html', scenariotest = all_data)


@main.route('/new-scenario', methods=['GET'])    
def new_scenario():
    return render_template('new-scenario.html')


@main.route('/view-scenario', methods=['GET'])    
def view_scenario():
    id = request.args.get('id')
    return render_template('new-scenario.html', scenario_id=id)


@main.route('/new-test/<id>', methods=['GET'])   
def new_test(id):
    return render_template('new-test.html', suniukas=id)


@main.route('/results', methods=['GET'])
def results():
    all_data = Results.query.all()
    return render_template('results.html', results = all_data)


# @main.route('/testing-ajax', methods=['GET'])
# def testing_alax():
#     all_data = ScenarioTest.query.all()

#     data = {}                                                                                            
#     data['data']=[]
    
#     for item in all_data:
#         obj = {   
#             "id": item.id,
#             "date": str(item.date),
#             "source": item.source,
#             "destination": item.destination,
#             "program": item.program,
#             "duration": item.duration,
#             "protocol": item.protocol,
#             "num_streams": item.num_streams,
#             "throughput": item.throughput,
#             "mss": item.mss,
#             "tos": item.tos,
#             "scenario_id": item.scenario_id
#         }
   
#         data['data'].append(obj)

#     return jsonify(data)


@main.route('/login', methods=['POST'])
def login_user():
    vardas = request.form['vardas']
    password = request.form['password']

    user = db.session.query(User).filter_by(username=vardas).first()

    if (user is not None and check_password_hash(user.password,password)):

        return render_template('home.html')
    else:
        return "Klaida. Prasome pasitikrinti vartotojo varda ar slaptazodi"


@main.route('/login-submit', methods=['POST'])
def login_submit():
    if request.method == 'POST':
        vardas = request.form['vardas']
        password = request.form['password1']
        password_repeat = request.form['password2']

        user = db.session.query(User).filter_by(username=vardas).first()

        if (password==password_repeat):

            if (user != None):
                return "Toks vartotojas jau egzistuoja. Prasome bandyti dar karta"

            new_user = User()
            new_user.username = vardas
            new_user.password = generate_password_hash(password,'sha256')

            db.session.add(new_user)
            db.session.commit()

            return render_template('index.html')
        else:
            return "Slaptazodziai nesutampa"
    return "Klaida"


@main.route('/scenario-submit', methods=['POST'])
def scenario_submit():
    if request.method == 'POST':
        user_id = current_user.get_id()
        new_id =str(uuid.uuid4())
        new_scenario = Scenario(id=new_id)

        db.session.add(new_scenario)
        db.session.commit()

    return render_template('new-scenario.html', scenario_id=new_scenario.id)


@main.route('/testing-submit', methods=['POST'])
def testing_submit():

    if request.method == 'POST':
        scenario_id = request.form['scenario_id']
        date = request.form['datetime']
        source = request.form['source']
        destination = request.form['destination']
        program = request.form['program']
        duration = request.form['duration']
        protocol = request.form['protocol']
        num_streams = request.form['num_streams']
        throughput = request.form['throughput']
        mss = request.form['mss']
        tos = request.form['tos']
        
        new_id = str(uuid.uuid4())
        new_test = ScenarioTest(scenario_id=scenario_id, id=new_id, date=date, source=source, destination=destination, program=program, duration=duration, protocol=protocol, num_streams=num_streams, throughput=throughput, mss=mss, tos=tos)
                                  
        db.session.add(new_test)  
        db.session.commit()

    return redirect(url_for('main.view_scenario', id=scenario_id))

    
def run_json(scenario_id, new_id, date, program, source, destination, duration, protocol, num_streams, throughput, mss, tos, params): #CIA GALI TEKTI PAPILDYTI
    senmsg = {
        "scenario": {
            "id": scenario_id,
            "test": {
                "id": new_id,
                    "date": str(date),
                    "source": source,
                    "destination": destination,
                    "program": program,
                    "duration": duration,
                    "protocol": protocol,
                    "num_streams": num_streams,
                    "throughput": throughput,
                    "mss": mss,
                    "tos": tos,
                    "params": params
                }
        }
    }

    print(senmsg)
    senmsg = json.dumps(senmsg, indent=4)  
    return senmsg
   

#Istrinti ScenarioTest   
@main.route('/delete/<id>/', methods = ['GET', 'POST'])
def delete(id):
    new_test = ScenarioTest.query.get(id)
    db.session.delete(new_test)
    db.session.commit()
    return redirect(url_for('main.testing'))


#Paleisti ScenarioTest
@main.route('/run/<id>/', methods = ['GET', 'POST'])
def run(id):
    test = ScenarioTest.query.get(id)
    params ='-c ' + test.destination + ' '
    if test.protocol == 'UDP':
        params += '-u '
    if test.num_streams:
        params += '-P ' + test.num_streams + ' '
    if test.duration:
        params += '-t ' + test.duration + ' '
    if test.throughput:
        params += '-b ' + test.throughput + 'm' + ' '
    if test.mss:
        params += '-M ' + test.mss + ' '
    if test.tos:
        params += '-S ' + test.tos + ' '
    

    payload = run_json(test.scenario_id, test.id, test.date, test.program, test.source, test.destination, test.duration, test.protocol, test.num_streams, test.throughput, test.mss, test.tos, params)

    print("SMN/network/" + test.source)
    print("Suformuota zinute:")
    print(payload)

    topic = "SMN/network/" + test.source
    publish_command(topic, payload)

    return redirect(url_for('main.testing'))


def publish_command(topic, command):
        publish.single(
            topic=topic,
            payload=command,
            hostname=broker_address, 
            port=port
        )
        #print('I mosquitto: ', command)
        return 'Sekme'

        

