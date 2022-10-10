import time
import logging
from tqdm import tqdm

from modules.bioreactor import Bioreactor
from modules.media_supply_box import MediaSupplyBox

logging.getLogger('opcua').setLevel(logging.CRITICAL)
logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s [%(module)s.%(funcName)s]',
                    datefmt='%Y-%m-%d %H:%M:%S', level=logging.INFO)


if __name__ == '__main__':
    logging.info(f'====Initialisation====')
    bioreactor = Bioreactor()
    media_supply_box = MediaSupplyBox()

    exp_duration = 3

    doe = pd.read_csv('../doe/doe_2022-08-16.csv')
    doe.reset_index()
    total_number_exp = len(doe)

    logging.info(f'====Experiments====')
    for exp_no, exp_data in doe.iterrows():
        logging.info(f'====Experiment {exp_no}====')

        bioreactor.bioreactor.connect()
        bioreactor.agitate_start(rpm=exp_data['Stirrer speed'])
        bioreactor.bioreactor.disconnect()

        media_supply_box.media_supply_box.connect()
        media_supply_box.gas_feed_start(gas_flow=exp_data['Volume flow rate'])
        media_supply_box.media_supply_box.disconnect()

        for i in tqdm(range(0, int(exp_duration)), desc=f"Experiment execution: {exp_no}/{total_number_exp}"):
            time.sleep(1)

        bioreactor.bioreactor.connect()
        bioreactor.agitate_stop()
        bioreactor.bioreactor.disconnect()

        media_supply_box.media_supply_box.connect()
        media_supply_box.gas_feed_stop()
        media_supply_box.media_supply_box.disconnect()

    logging.info(f'====Finishing====')
    bioreactor.bioreactor.connect()
    bioreactor.reset_all_services()
    bioreactor.bioreactor.disconnect()

    media_supply_box.media_supply_box.connect()
    media_supply_box.reset_all_services()
    media_supply_box.media_supply_box.disconnect()
