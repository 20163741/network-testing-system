import paho.mqtt.client as mqtt  # import the client1
import math


#Laiko ir datos bibliotekos
import time
import datetime
from datetime import date

#JSON
import json

from time import ctime
import subprocess
import sys

import threading
import random
import pymysql
import sqlalchemy
from sqlalchemy import create_engine
import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime
from uuid import uuid4

Base = declarative_base()

class Results(Base):
    __tablename__ = 'results'

    scenario_id = Column(String(36), primary_key=True)
    id = Column(String(36), nullable=False)
    date = Column(DateTime, nullable=False) 
    program = Column(String(40), nullable=False)
    source = Column(String(40), nullable=True)
    destination = Column(String(40), nullable=True) 
    protocol = Column(String(40), nullable=True)
    duration = Column(String(40), nullable=True)
    num_streams = Column(String(40), nullable=True) 
    throughput = Column(String(40), nullable=True)
    mss = Column(String(40), nullable=True)
    tos = Column(String(40), nullable=True)
    bits_per_second = Column(String(40), nullable=True) # TCP pralaidumas
    lost_percent = Column(String(40), nullable=True)
    jitter_ms = Column(String(40), nullable=True)


# ------------------- PIRPMINIAI DUOMENYS -----------------

port = 1883
sub_topic = "SMN/network/TestResults"
garanted_qos = 2
broker_address = '10.128.67.37'
UUID = "7c925d9c-b331-4854-aacb-47c9aa9srsrv"

client = mqtt.Client(UUID)

engine = db.create_engine('mysql+pymysql://root:areta@localhost:3306/network-testing-db')
connection = engine.connect()
metadata = db.MetaData()
rezultsDBTable = db.Table('results', metadata, autoload=True, autoload_with=engine)
# ----------------------------------------------------------------------------

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Prisijungta sekmingai, grazinamas kodas =", rc)
    else:
        print("Nepavyko prisijungti, grazinamas kodas =", rc)


def on_subscribe(client, userdata, mid, garanted_qos):
    print("Prenumeruojama su QoS", garanted_qos)


def on_message(client, userdata, message):
    print("Gauta zinute " + str(message.payload.decode("utf-8")))
    rez = str(message.payload.decode())
    finish = json.loads(rez)
    print(finish)


    protocol = finish['results']['start']['test_start']['protocol']
    print ('-------------------------------------------')


    if protocol == 'TCP':
        scenario_id = finish['scenario_id']
        id = finish['test_id']
        date = finish['date']
        program = finish['program']
        source = finish['source']
        destination = finish['destination']  #test_id
        protocol = finish['results']['start']['test_start']['protocol']
        #protocol = finish['protocol']
        duration = finish['duration']
        num_streams = finish['num_streams']
        tos = finish['tos']
        mss = finish['mss']
        bits_per_second = finish['results']['end']['sum_received']['bits_per_second']

        print(scenario_id)
        print(id)
        print(date)
        print(program)
        print(source)
        print(destination)
        print(protocol)
        print(duration)
        print(num_streams)
        print(tos)
        print(mss)

        bits_per_second = bits_per_second/1000000

        print(bits_per_second)
        print ('RRRR1')
        



        query = db.insert(rezultsDBTable).values(scenario_id=scenario_id, id=id, date=date, program=program, source=source, destination=destination, protocol=protocol, duration=duration, num_streams=num_streams, tos=tos, mss=mss, bits_per_second=bits_per_second)
        print ('ZRRRRR2')
    else:
        scenario_id = finish['scenario_id']
        id = finish['test_id']
        date = finish['date']
        program = finish['program'] #test_id
        source = finish['source']
        destination = finish['destination']
        protocol = finish['protocol']
        duration = finish['duration']
        num_streams = finish['num_streams']
        throughput = finish['throughput']
        tos = finish['tos']
        lost_percent = finish['results']['end']['sum']['lost_percent']
        jitter_ms = finish['results']['end']['sum']['jitter_ms']

        print(scenario_id)
        print(id)
        print(date)
        print(program)
        print(source)
        print(destination)
        print(protocol)
        print(duration)
        print(num_streams)
        print(tos)
        print(throughput)

        print(jitter_ms)
        print(lost_percent)
        print ('tcp1')
        
        query = db.insert(rezultsDBTable).values(scenario_id=scenario_id, id=id, date=date, program=program, source=source, destination=destination, protocol=protocol, duration=duration, num_streams=num_streams, tos=tos, throughput=throughput, jitter_ms=jitter_ms, lost_percent=lost_percent) 
        print ('tcp2')

    print ('Siunciam sql')
    ResultProxy = connection.execute(query)
    print (ResultProxy)


#=====================================================================


def on_message_print(client, userdata, message):
    print("%s %s" % (message.topic, message.payload.decode("utf-8")))


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Netiketas atsijungimas")
    else:
        print("Klientas atsijunge sekmingai")


def main ():
    # Konfiguruojam MQTT
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_message_print = on_message_print
    client.on_disconnect = on_disconnect

    # Jungiames prie brokerio
    client.connect(broker_address, port)

    print("Prenumeruojama tema", sub_topic)
    client.subscribe(sub_topic, qos=2)  # Klausosi SMN/network/TestResults temos

    client.loop_forever()
    print ('Pabaiga')

if __name__ == '__main__':
    main ()
                                            