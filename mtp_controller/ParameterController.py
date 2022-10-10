import logging
import time
from opcua import ua, Client


class ParameterController:
	def __init__(self, pea_name: str, parameter_name: str, pea_opcua_server: Client,
	             opcua_node_ids, time_delay=0.5):
		self.pea_name = pea_name
		self.parameter_name = parameter_name
		self.opcua_client = pea_opcua_server
		self.time_delay = time_delay
		self.opcua_node_ids = opcua_node_ids
		self.opcua_nodes = {}

		self.check_opcua_nodes_dict(opcua_node_ids)

		for opcua_node_var, opcua_node_id in opcua_node_ids.items():
			self.opcua_nodes[opcua_node_var] = self.opcua_client.get_node(opcua_node_id)

		self.set_operator()

	def check_opcua_nodes_dict(self, opcua_nodes):
		required_keys = ['StateOpOp', 'StateOffOp', 'StateOpAct', 'StateOffAct', 'VOp']
		for required_key in required_keys:
			if required_key not in opcua_nodes:
				logging.error(
					f'-- {self.pea_name}, {self.parameter_name}: Required key {required_key} not found in dict opcua_node_ids')
				raise Exception(f'Input parameter fopcua_node_ids does not contain all required keys: {required_keys}')

	def set_parameter_to_mode(self, mode: str):
		logging.debug(f'-- {self.pea_name}, {self.parameter_name}: Setting opmode to {mode}...')
		if mode == 'offline':
			self.opcua_nodes['StateOffOp'].set_value(True)
		elif mode == 'operator':
			self.opcua_nodes['StateOpOp'].set_value(True)
		time.sleep(self.time_delay)
		logging.debug(f'-- {self.pea_name}, {self.parameter_name}: OpMode is {self.get_opmode()}...')

	def set_offline(self):
		if self.get_opmode() is not 'offline':
			logging.debug(f'-- {self.pea_name}, {self.parameter_name}: Setting opmode to offline...')
			self.set_parameter_to_mode('offline')

	def set_operator(self):
		if self.get_opmode() is not 'operator':
			logging.debug(f'-- {self.pea_name}, {self.parameter_name}: Setting opmode to operator...')
			self.set_parameter_to_mode('operator')

	def get_opmode(self):
		if self.opcua_nodes['StateOpAct'].get_data_value().Value.Value:
			return 'operator'
		elif self.opcua_nodes['StateOffAct'].get_data_value().Value.Value:
			return 'offline'

	def set_value(self, set_value):
		logging.info(f'-- {self.pea_name}, {self.parameter_name}: Setting value to {set_value}...')
		self.set_operator()
		self._set_vop(set_value)

	def _set_vop(self, set_value):
		if isinstance(set_value, int):
			value_type = ua.VariantType.UInt32
		elif isinstance(set_value, float):
			value_type = ua.VariantType.Float
		else:
			return
		set_value = ua.Variant(set_value, value_type)
		self.opcua_nodes['VOp'].set_value(set_value)
		time.sleep(self.time_delay)
