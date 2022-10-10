import logging
import time
from opcua import Client
from mtp_controller.ServiceController import ServiceController


class PEAController:
    def __init__(self, pea_name, opcua_address, opcua_user='', opcua_password='', time_delay=0.2):
        self.pea_name = pea_name
        self.opcua_address = opcua_address
        self.opcua_user = opcua_user
        self.opcua_password = opcua_password
        self.opcua_client = Client(opcua_address, timeout=3)
        self.opcua_client.set_user(opcua_user)
        self.opcua_client.set_password(opcua_password)
        self.time_delay = time_delay
        self.connect()

        self.services = {}

    def connect(self):
        self.disconnect()
        time.sleep(self.time_delay)
        self.opcua_client.connect()
        time.sleep(self.time_delay)
        logging.debug(f'-- {self.pea_name}: Connected to OPC UA --')

    def disconnect(self):
        try:
            self.opcua_client.disconnect()
            time.sleep(self.time_delay)
            logging.debug(f'-- {self.pea_name}: Disconnected from OPC UA --')
        except:
            pass

    def is_connected(self):
        try:
            self.opcua_client.send_hello()
            return True
        except:
            return False

    def add_service(self, service_name, service_opcua_node_ids):
        self.services[service_name] = ServiceController(self.pea_name,
                                                        service_name,
                                                        self.opcua_client,
                                                        service_opcua_node_ids,
                                                        time_delay=self.time_delay)

    def add_parameter_to_service(self, service_name, parameter_name, parameter_opcua_node_ids):
        self.services[service_name].add_parameter(parameter_name, parameter_opcua_node_ids)

    #def run_step(self, service_name, parameter_name=None, parameter_value=None):
    #    self.services[service_name].change_configuration_parameter(parameter_name, parameter_value)
