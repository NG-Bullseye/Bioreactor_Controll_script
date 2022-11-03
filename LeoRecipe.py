import time
import json
from tqdm import tqdm
import logging
from modules.bioreactor import Bioreactor
from modules.media_supply_box import MediaSupplyBox
import socket
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
    {'gas_flow': 75, 'rpm': 100},  # loaded
]

# funktion zur abbildung von rpm und gasflow nach flow regime siehe Corina Kröger gleichung parameter dynamisch mit
# random faktor ändern aber so dass das flowregime stabil bleibt. Erste und letzte bilder entfernnen. extra perioden
# für übergangsregime einführen

exp_no = 0
picturesPersecond = 4
picturesTaken = 0
amountOfPicutures = 4



# Expose 1355933 1300000.00  µs
# gammma= 0.63 0.64

# Exposure 5653.00
# gamma 0.39

#2660 per state
#6188
# while amountOfPicutures <= picturesTaken: # repeats until the amount of pictures where taken.
#  print(f'====RESTART EXPERIMENTS====')
timestamp_mask = []
timestamp_maskLabel = []


s = socket.socket()
host = "10.6.51.140"  # "127.0.1.1" camera ip
port = 8000  # Make sure it's within the > 1024 $$ <65535 range

#########################################################################################################################################################################
process_setup_duration = 5  # 5
exp_duration = 6  # 6 sec
process_end = 2
ENABLED_TCP_CAMERA_SERVER = True
amountOfExperimentsPerRegime = 200
#########################################################################################################################################################################
#6063 2.16 0.52
randomExps = ProcessParameterInFlowRegimes.getExperiments(amountOfExperimentsPerRegime) # 0:Dispersded, 1:Transistion, 2:Loaded, 3:Flooded
ProcessParameterInFlowRegimes.plot()
if ENABLED_TCP_CAMERA_SERVER:
    s.connect((host, port))
    s.send("pause".encode('utf-8'))
    data = s.recv(1024).decode('utf-8')
    print('Server Confirmed: ' + data)
for i in range(0, 4):
    label_timestamp_begin = int(time.time() * 1000)
    for exp in randomExps[i]:
        try:
            exp_no += 1
            print (f"                                        ======== NUMBER {exp_no}  ========")
            logging.info(f'====Experiment {exp}====')

            bioreactor.bioreactor.connect()
            bioreactor.agitate_start(rpm=exp['rpm'])
            bioreactor.bioreactor.disconnect()

            media_supply_box.media_supply_box.connect()
            media_supply_box.gas_feed_start(gas_flow=exp['gas_flow'])
            media_supply_box.media_supply_box.disconnect()

            time.sleep(process_setup_duration)
            if ENABLED_TCP_CAMERA_SERVER:
                s.send("resume".encode('utf-8'))
                data = s.recv(1024).decode('utf-8')
                print('Server Confirmed: ' + data)
            timestamp_begin = int(time.time() * 1000)
            #if not first_timestamp:
             #   first_timestamp = timestamp_begin

            #print("Experiment will Terminate at ", datetime.strptime(datetime.now()+timedelta(milliseconds=(timestamp_begin - first_timestamp)*amountOfExperimentsPerRegime*4/ exp_no/60), '%d/%m/%Y %H:%M:%S.%f'))

            for i in tqdm(range(0, int(exp_duration)), desc=f"Experiment execution: {exp_no}/{len(experiments)}"):
                time.sleep(1)
            timestamp_end = int(time.time() * 1000)
            if ENABLED_TCP_CAMERA_SERVER:
                s.send("pause".encode('utf-8'))
                data = s.recv(1024).decode('utf-8')
                print('Server Confirmed: ' + data)
            timestamp_mask.append({'begin': timestamp_begin, 'end': timestamp_end})

            time.sleep(process_end)

            bioreactor.bioreactor.connect()
            bioreactor.agitate_stop()
            bioreactor.bioreactor.disconnect()

            media_supply_box.media_supply_box.connect()
            media_supply_box.gas_feed_stop()
            media_supply_box.media_supply_box.disconnect()
        except:
            while True:
                try:
                    bioreactor.bioreactor.connect()
                    bioreactor.agitate_stop()
                    bioreactor.bioreactor.disconnect()

                    media_supply_box.media_supply_box.connect()
                    media_supply_box.gas_feed_stop()
                    media_supply_box.media_supply_box.disconnect()
                    break
                except:
                    print("cant connect to media box. Trying again.")

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
if ENABLED_TCP_CAMERA_SERVER:
    s.send("stop".encode('utf-8'))
    data = s.recv(1024).decode('utf-8')
    print('Server Confirmed: ' + data)
