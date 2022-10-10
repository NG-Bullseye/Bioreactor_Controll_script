import random
import time
import json

import numpy as np
import numpy
from tqdm import tqdm
import logging

from modules.bioreactor import Bioreactor
from modules.media_supply_box import MediaSupplyBox

import ProcessParameterInFlowRegimes

logging.getLogger('opcua').setLevel(logging.CRITICAL)
logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s [%(module)s.%(funcName)s]',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)


TIME_DELAY = 0.5
RECONNECT_REQUIRED = True

print(f'====Initialisation====')
media_supply_box = MediaSupplyBox()
bioreactor = Bioreactor()


experiments = [
    {'gas_flow': 50, 'rpm': 200},
    {'gas_flow': 75, 'rpm': 100},#loaded
  ]

#funktion zur abbildung von rpm und gasflow nach flow regime siehe Corina Kröger gleichung
# parameter dynamisch mit random faktor ändern aber so dass das flowregime stabil bleibt. Erste und letzte bilder entfernnen.
# extra perioden für übergangsregime einführen

exp_no = 0
picturesPersecond = 4
picturesTaken = 0
amountOfPicutures = 4

process_setup_duration = 5 #5
exp_duration = 6 #6 sec
process_end = 2

#Expose 1355933 1300000.00  µs
#gammma= 0.63 0.64

#Exposure 5653.00
#gamma 0.39


#while amountOfPicutures <= picturesTaken: # repeats until the amount of pictures where taken.
#  print(f'====RESTART EXPERIMENTS====')
timestamp_mask = []
timestamp_maskLabel = []

randomExps =  ProcessParameterInFlowRegimes.getExperiments()[1] #0:Dispersded, 1:Transistion, 2:Loaded, 3:Flooded

ProcessParameterInFlowRegimes.plot()

expMax = [{'rpm': 1000, 'gas_flow': 150}]
expMin = [{'rpm': 100, 'gas_flow': 10}]

expDisp= [{'rpm': 750, 'gas_flow': 80}]
expTrans= [{'rpm': 650, 'gas_flow': 80}]
expLoad= [{'rpm': 480, 'gas_flow': 80}]
expFlo= [{'rpm': 226, 'gas_flow': 80}]
                            #MAX                        #Flooded                        #Loaded                     #Trans                      #Early Disp                 #disp                       #MAX
lowGas=[{'rpm': 1000, 'gas_flow': 20},{'rpm': 150, 'gas_flow': 20}  ,{'rpm': 300, 'gas_flow': 20}   ,{'rpm': 450, 'gas_flow': 20},{'rpm': 570, 'gas_flow': 20}   ,{'rpm': 770, 'gas_flow': 20},{'rpm': 1000, 'gas_flow': 20}]

midGas=[{'rpm': 1000, 'gas_flow': 80},{'rpm': 226, 'gas_flow': 80}  ,{'rpm': 480, 'gas_flow': 80}   ,{'rpm': 650, 'gas_flow': 80},{'rpm': 860, 'gas_flow': 80}   ,{'rpm': 850, 'gas_flow': 80},{'rpm': 1000, 'gas_flow': 80}]
highGas=[{'rpm': 1000, 'gas_flow': 140},{'rpm': 277, 'gas_flow': 140} ,{'rpm': 550, 'gas_flow': 140}  ,{'rpm': 750, 'gas_flow': 140},{'rpm': 950, 'gas_flow': 140},{'rpm': 900, 'gas_flow': 140},{'rpm': 1000, 'gas_flow': 140}]

             #high lowgas                   #min high gas               # min low gas                    # high high gas
kriticaltransifitons=[{'rpm': 770, 'gas_flow': 20},{'rpm': 277, 'gas_flow': 140},{'rpm': 150, 'gas_flow': 20},{'rpm': 900, 'gas_flow': 140}]
                              #Trans    high             #Early Disp high                     #Trans mid           #Early Disp mid                   #Trans low             #Early Disp low
transDisphighmidlow=[{'rpm': 780, 'gas_flow': 140},{'rpm': 820, 'gas_flow': 140},{'rpm': 695, 'gas_flow': 80},{'rpm': 735, 'gas_flow': 80},{'rpm': 520, 'gas_flow': 22},{'rpm': 560, 'gas_flow': 20}]
transedge=[{'rpm': 780, 'gas_flow': 140},{'rpm': 695, 'gas_flow': 80},{'rpm': 520, 'gas_flow': 22}]
dispEdge=[{'rpm': 820, 'gas_flow': 140},{'rpm': 735, 'gas_flow': 80},{'rpm': 560, 'gas_flow': 20}]



nani=[{'rpm': 780, 'gas_flow': 140},{'rpm': 820, 'gas_flow': 140}]
for i in range(0,4):
    label_timestamp_begin = int(time.time() * 1000)
    for exp in ProcessParameterInFlowRegimes.getExperiments()[0]:
        exp_no += 1
        print(f'====Experiment {exp}====')

        logging.info(f'====Experiment {exp_no}====')

        bioreactor.bioreactor.connect()
        bioreactor.agitate_start(rpm=exp['rpm'])
        bioreactor.bioreactor.disconnect()

        media_supply_box.media_supply_box.connect()
        media_supply_box.gas_feed_start(gas_flow=exp['gas_flow'])
        media_supply_box.media_supply_box.disconnect()

        time.sleep(process_setup_duration)

        timestamp_begin = int(time.time()*1000)
        for i in tqdm(range(0, int(exp_duration)), desc=f"Experiment execution: {exp_no}/{len(experiments)}"):
            time.sleep(1)
        timestamp_end = int(time.time()*1000)

        timestamp_mask.append({'begin': timestamp_begin, 'end': timestamp_end})

        time.sleep(process_end)

        bioreactor.bioreactor.connect()
        bioreactor.agitate_stop()
        bioreactor.bioreactor.disconnect()

        media_supply_box.media_supply_box.connect()
        media_supply_box.gas_feed_stop()
        media_supply_box.media_supply_box.disconnect()

        picturesTaken = picturesTaken + picturesPersecond*exp_duration
    label_timestamp_end = int(time.time() * 1000)
    timestamp_maskLabel.append({'begin': label_timestamp_begin, 'end': label_timestamp_end})
    with open('ExpermientTimestamps.json', 'w') as f:
        json.dump(timestamp_mask, f)
    logging.info(f'====FLOWREGIME FINISHED====')

with open('LabelTimestamps.json', 'w') as f:
    json.dump(timestamp_maskLabel, f)
logging.info(f'====FINISHING====')


bioreactor.bioreactor.connect()
bioreactor.reset_all_services()
bioreactor.bioreactor.disconnect()

media_supply_box.media_supply_box.connect()
media_supply_box.reset_all_services()
media_supply_box.media_supply_box.disconnect()
