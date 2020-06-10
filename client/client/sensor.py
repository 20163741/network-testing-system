import paho.mqtt.client as mqtt  # import the client
import iperf3
from datetime import date

#Laiko ir datos bibliotekos
import time
import datetime
import dateutil.parser 
from time import ctime  

#JSON
import json

import subprocess
import sys

import threading
import random

# ------------------- PIRMINIAI DUOMENYS -----------------

port = 1883   
sub_topic = "SMN/network/10.128.67.66"
# sub_topic = "SMN/network/IP(10.128.67.38/10.128.67.66/10.128.67.82/10.128.67.83)" Kiekvienam jutikliui atskirai nurodomas jo IP adresas
pub_topic = "SMN/network/TestResults"  
garanted_qos = 2
broker_address = '10.128.67.37'
UUID = "7c925d9c-b331-4854-aacb-47c9aa922222"

client = mqtt.Client(UUID)
testthreads = []

# -------------------- FUNKCIJOS ATGALINIAM RYSIUI ----------------------


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Prisijungta sekmingai, grazinamas kodas =", rc)
    else:
        print("Nepavyko prisijungti, grazinamas kodas =", rc)


def on_subscribe(client, userdata, mid, garanted_qos):  
    print("Prenumeruojama su QoS", garanted_qos) 


def startPing(cli):
    print ('Ping')
    process = subprocess.Popen(['ping', '-c 5', '127.0.0.1'], 
                               stdout=subprocess.PIPE,
                               universal_newlines=True)

    while True:
        output = process.stdout.readline()
        print(output.strip())
       
        return_code = process.poll()
        if return_code is not None:
            print('Grazinamas kodas', return_code)  

            for output in process.stdout.readlines():
                print(output.strip())
            break    
    return 0


def startIperf3(cli):
    print ('Pradedamas iperf3 procesas....')

    command = ['iperf3']
    # Rezultatus isvedame JSON, todel pridedame -J
    command.extend(['-J'])
    # Prijungiame parametrus, kuriuos atsiunte is serverio
    command.extend(cli.split(' '))
    print ('CLI:', cli)
    print ('Komanda:', command)
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    # Laukiame kol baigsis programa
    while True:
        exitCode = process.poll()
        if exitCode is not None:
            break
    # Tikriname, koks programos isejimo kodas. Unix'e 0 - viskas OK
    # <> 0 - klaida
    if exitCode == 0:
        return process.stdout.read()
    else:
        return -1


def startMeasurement(initData):
    print ('Pradedama gija')
    # Susideliojame duomenis
    scenarioID = initData['scenario']['id']
    testID = initData['scenario']['test']['id']
    testDate = initData['scenario']['test']['date']
    testProgram = initData['scenario']['test']['program']
    testSource = initData['scenario']['test']['source']
    testDestination = initData['scenario']['test']['destination']
    testProtocol = initData['scenario']['test']['protocol']
    testDuration = initData['scenario']['test']['duration']
    testNum_streams = initData['scenario']['test']['num_streams']
    testThroughput = initData['scenario']['test']['throughput']
    testMss = initData['scenario']['test']['mss']
    testTos = initData['scenario']['test']['tos']
    testString = initData['scenario']['test']['params']

    # Issivedame i ekrana uzduoti
    print ('Scenario ID: ', scenarioID, ' Test ID: ', testID, ' Start date and time: ', testDate)
    print ('Test string: ', testProgram, testString)

    print (datetime.datetime.now())
    print (dateutil.parser.parse(testDate))
    
    # Laukiame kol ateis laikas
    while datetime.datetime.now() <= dateutil.parser.parse(testDate):
        time.sleep (1) 

    # Atejo laikas daryti testus
    print ('Pradedamas testavimas....')

    if testProgram == 'iperf3':
        results = startIperf3(testString) 
    elif testProgram == 'ping':
        results = startPing(testString) 

    results_json = {
        "scenario_id": scenarioID,
        "test_id": testID,
        "date": testDate,
        "source": testSource,
        "destination": testDestination,
        "protocol": testProtocol,
        "duration": testDuration,
        "program": testProgram,
        "num_streams": testNum_streams,        
        "throughput": testThroughput,
        "mss": testMss,
        "tos": testTos,
        "results": json.loads(results)
    }

    results_json = json.dumps(results_json, indent=4) 
    # Siunciame rezultatus
    if results != -1: 
        client.publish(pub_topic, results_json, qos=2)
    else:
        print ('Ivyko klaida')
    return 0


def on_message(client, userdata, message):
    print("Gauta zinute " + str(message.payload.decode("utf-8")))
    print('Pradedama')
    data = str(message.payload.decode())
    ms = json.loads(data)
    print(ms)
    print(ms['scenario']['test']['date'])
    currentthread=threading.Thread(target=startMeasurement, args=(ms,))
    testthreads.append(currentthread)
    currentthread.start()
    print ('Veikianciu giju skaicius: ', len(testthreads))


def on_message_print(client, userdata, message):
    print("%s %s" % (message.topic, message.payload.decode("utf-8")))


def on_publish(client, userdata, mid):  
    print("Duomenys paskelbti su pranesimo id =", mid)  #mid yra Message ID


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Netiketas atsijungimas")
    else:
        print("Klientas atsijunge sekmingai")


def main ():
    # konfiguruojam MQTT
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.on_message_print = on_message_print
    client.on_publish = on_publish
    client.on_disconnect = on_disconnect

    # Jungiames prie brokerio
    client.connect(broker_address, port)  

    print("Prenumeruojama tema", sub_topic)
    client.subscribe(topic=sub_topic, qos=2)  # Klausosi SMN/network/sensorx temos

    client.loop_forever()
    print ('Pabaiga')

if __name__ == '__main__':
    main ()

