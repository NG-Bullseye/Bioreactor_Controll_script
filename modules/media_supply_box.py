from mtp_controller.PEAController import PEAController
import time


class MediaSupplyBox:
    def __init__(self):
        self.media_supply_box = PEAController(pea_name='M00_MediaSupplyBox',
                                              opcua_address='opc.tcp://10.6.51.201:4840/',
                                              opcua_user='',
                                              opcua_password='')

        self.add_service_gas_control()
        self.reset_all_services()

    def add_service_gas_control(self):
        service_common = 'ns=2;s=Volumeflow_basedGasFeedControl_'
        gas_control_opcua_nodes = {
            'StateOpOp': service_common + 'StateOpOp',
            'StateOffOp': service_common + 'StateOffOp',
            'StateOpAct': service_common + 'StateOpAct',
            'StateOffAct': service_common + 'StateOffAct',
            'CommandOp': service_common + 'CommandOp',
            'StateCur': service_common + 'StateCur',
        }
        self.media_supply_box.add_service('gas_control', gas_control_opcua_nodes)

        parameter_common = 'ns=2;s=Volumeflow_basedGasFeed_Continuous_SetVolumeflow_'
        gas_control_setpoint_opcua_nodes = {
            'StateOpOp': parameter_common + 'StateOpOp',
            'StateOffOp': parameter_common + 'StateOffOp',
            'StateOpAct': parameter_common + 'StateOpAct',
            'StateOffAct': parameter_common + 'StateOffAct',
            'VOp': parameter_common + 'VOp',
        }
        self.media_supply_box.add_parameter_to_service('gas_control', 'set_point', gas_control_setpoint_opcua_nodes)

    def gas_feed_start(self, gas_flow):
        self.media_supply_box.services['gas_control'].change_configuration_parameter('set_point', float(gas_flow))
        self.media_supply_box.services['gas_control'].run()
        time.sleep(2)

    def gas_feed_stop(self):
        self.media_supply_box.services['gas_control'].reset_state_to_idle()

    def reset_all_services(self):
        self.media_supply_box.services['gas_control'].reset_state_to_idle()
