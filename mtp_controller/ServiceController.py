import logging
import time
from opcua import ua, Client
from mtp_controller.ParameterController import ParameterController


class ServiceController:
    def __init__(self, pea_name: str, service_name: str,
                 pea_opcua_server: Client,
                 opcua_node_ids, time_delay=0.5):
        self.pea_name = pea_name
        self.service_name = service_name
        self.opcua_client = pea_opcua_server
        self.time_delay = time_delay
        self.opcua_node_ids = opcua_node_ids
        self.opcua_nodes = {}
        self.check_opcua_nodes_dict(opcua_node_ids)
        for opcua_node_var, opcua_node_id in opcua_node_ids.items():
            self.opcua_nodes[opcua_node_var] = self.opcua_client.get_node(opcua_node_id)

        self.service_parameters = {}

    def check_opcua_nodes_dict(self, opcua_nodes):
        required_keys = ['StateOpOp', 'StateOffOp', 'StateOpAct', 'StateOffAct', 'CommandOp', 'StateCur']
        for required_key in required_keys:
            if required_key not in opcua_nodes:
                logging.error(f'-- {self.pea_name}: Required key {required_key} not found in dict opcua_node_ids')
                raise Exception(f'Input parameter fopcua_node_ids does not contain all required keys: {required_keys}')

    def set_service_to_mode(self, mode: str):
        logging.debug(f'-- {self.pea_name}, {self.service_name}: Setting opmode to {mode}...')
        if mode == 'offline':
            self.opcua_nodes['StateOffOp'].set_value(True)
        elif mode == 'operator':
            self.opcua_nodes['StateOpOp'].set_value(True)
        time.sleep(self.time_delay)
        logging.debug(f'-- {self.pea_name}, {self.service_name}: OpMode is {self.get_opmode()}...')

    def set_offline(self):
        if self.get_opmode() != 'offline':
            logging.debug(f'-- {self.pea_name}, {self.service_name}: Setting opmode to offline...')
            self.set_service_to_mode('offline')

    def set_operator(self):
        if self.get_opmode() != 'operator':
            logging.debug(f'-- {self.pea_name}, {self.service_name}: Setting opmode to operator...')
            self.set_service_to_mode('operator')

    def get_opmode(self):
        if self.opcua_nodes['StateOpAct'].get_data_value().Value.Value:
            return 'operator'
        elif self.opcua_nodes['StateOffAct'].get_data_value().Value.Value:
            return 'offline'

    def send_command(self, command: int):
        logging.debug(f'-- {self.pea_name}, {self.service_name}: Sending command {command}...')
        command = ua.Variant(command, ua.VariantType.UInt32)
        self.opcua_nodes['CommandOp'].set_value(command)
        time.sleep(self.time_delay)

    def start(self):
        logging.info(f'-- {self.pea_name}, {self.service_name}: Sending command start (4)...')
        self.send_command(4)

    def complete(self):
        logging.info(f'-- {self.pea_name}, {self.service_name}: Sending command complete (1024)...')
        self.send_command(1024)

    def abort(self):
        logging.info(f'-- {self.pea_name}, {self.service_name}: Sending command abort (1024)...')
        self.send_command(256)

    def reset(self):
        logging.info(f'-- {self.pea_name}, {self.service_name}: Sending command reset (2)...')
        self.send_command(2)

    def get_state(self):
        state = self.opcua_nodes['StateCur'].get_data_value().Value.Value
        logging.debug(f'-- {self.pea_name}, {self.service_name}: Current state is {state}')

    def reset_state_to_idle(self):
        if self.get_state() != 16:
            self.complete()
            time.sleep(self.time_delay)
            self.reset()
            time.sleep(self.time_delay)

    def add_parameter(self, parameter_name, parameter_opcua_node_ids):
        self.service_parameters[parameter_name] = ParameterController(self.pea_name,
                                                                      parameter_name,
                                                                      self.opcua_client,
                                                                      parameter_opcua_node_ids,
                                                                      time_delay=self.time_delay)

    def _set_configuration_parameter(self, parameter_name, value):
        if parameter_name not in self.service_parameters:
            logging.error(f'-- {self.pea_name}, {self.service_name} does not have parameter with name {parameter_name}')
            return
        self.service_parameters[parameter_name].set_value(value)

    def change_configuration_parameter(self, parameter_name=None, value=None):
        self.set_offline()
        if parameter_name != None:
            self._set_configuration_parameter(parameter_name, value)

    def run(self):
        self.set_operator()
        self.start()
