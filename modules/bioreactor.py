import time

from mtp_controller.PEAController import PEAController


class Bioreactor:
    def __init__(self):
        self.bioreactor = PEAController(pea_name='M04_Bioreactor',
                                        opcua_address='opc.tcp://10.6.51.40:4840/',
                                        opcua_user='admin',
                                        opcua_password='wago')

        self.add_service_calibrate_vessel()
        self.add_service_pressure_release()
        self.add_service_aerate()
        self.add_service_agitate()

        self.reset_all_services()

        self.calibrate_vessel()
        self.prepare_to_aeration()

    def add_service_calibrate_vessel(self):
        bioreactor_service_common = 'ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.TARE_1.ServiceControl'
        opcua_common_name_opcua_nodes = {
            'StateOpOp': bioreactor_service_common + '.StateOpOp',
            'StateOffOp': bioreactor_service_common + '.StateOffOp',
            'StateOpAct': bioreactor_service_common + '.StateOpAct',
            'StateOffAct': bioreactor_service_common + '.StateOffAct',
            'CommandOp': bioreactor_service_common + '.CommandOp',
            'StateCur': bioreactor_service_common + '.StateCur',
        }
        self.bioreactor.add_service('calibrate_vessel', opcua_common_name_opcua_nodes)

        bioreactor_parameter_common = 'ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.TARE_1.CP_TARE_SP'
        opcua_common_name_setpoint_opcua_nodes = {
            'StateOpOp': bioreactor_parameter_common + '.StateOpOp',
            'StateOffOp': bioreactor_parameter_common + '.StateOffOp',
            'StateOpAct': bioreactor_parameter_common + '.StateOpAct',
            'StateOffAct': bioreactor_parameter_common + '.StateOffAct',
            'VOp': bioreactor_parameter_common + '.VOp',
        }
        self.bioreactor.add_parameter_to_service('calibrate_vessel', 'calibration_setpoint',
                                                 opcua_common_name_setpoint_opcua_nodes)

    def add_service_pressure_release(self):
        bioreactor_service_common = 'ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.PRESSURE_RELEASE_1.ServiceControl'
        opcua_common_name_opcua_nodes = {
            'StateOpOp': bioreactor_service_common + '.StateOpOp',
            'StateOffOp': bioreactor_service_common + '.StateOffOp',
            'StateOpAct': bioreactor_service_common + '.StateOpAct',
            'StateOffAct': bioreactor_service_common + '.StateOffAct',
            'CommandOp': bioreactor_service_common + '.CommandOp',
            'StateCur': bioreactor_service_common + '.StateCur',
        }
        self.bioreactor.add_service('pressure_release', opcua_common_name_opcua_nodes)

    def add_service_aerate(self):
        bioreactor_service_common = 'ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.AIR_1.ServiceControl'
        opcua_common_name_opcua_nodes = {
            'StateOpOp': bioreactor_service_common + '.StateOpOp',
            'StateOffOp': bioreactor_service_common + '.StateOffOp',
            'StateOpAct': bioreactor_service_common + '.StateOpAct',
            'StateOffAct': bioreactor_service_common + '.StateOffAct',
            'CommandOp': bioreactor_service_common + '.CommandOp',
            'StateCur': bioreactor_service_common + '.StateCur',
        }
        self.bioreactor.add_service('aerate', opcua_common_name_opcua_nodes)

    def add_service_agitate(self):
        bioreactor_service_common = 'ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.AGIT_1.ServiceControl'
        opcua_common_name_opcua_nodes = {
            'StateOpOp': bioreactor_service_common + '.StateOpOp',
            'StateOffOp': bioreactor_service_common + '.StateOffOp',
            'StateOpAct': bioreactor_service_common + '.StateOpAct',
            'StateOffAct': bioreactor_service_common + '.StateOffAct',
            'CommandOp': bioreactor_service_common + '.CommandOp',
            'StateCur': bioreactor_service_common + '.StateCur',
        }
        self.bioreactor.add_service('agitate', opcua_common_name_opcua_nodes)

        bioreactor_parameter_common = 'ns=4;s=|var|WAGO 750-8212 PFC200 G2 2ETH RS.Application.Services.AGIT_1.CP_AGIT_SETPOINT_RPM'
        opcua_common_name_setpoint_opcua_nodes = {
            'StateOpOp': bioreactor_parameter_common + '.StateOpOp',
            'StateOffOp': bioreactor_parameter_common + '.StateOffOp',
            'StateOpAct': bioreactor_parameter_common + '.StateOpAct',
            'StateOffAct': bioreactor_parameter_common + '.StateOffAct',
            'VOp': bioreactor_parameter_common + '.VOp',
        }
        self.bioreactor.add_parameter_to_service('agitate', 'agitate_setpoint',
                                                 opcua_common_name_setpoint_opcua_nodes)

    def calibrate_vessel(self):
        self.bioreactor.services['calibrate_vessel'].change_configuration_parameter('calibration_setpoint', 30.0)
        self.bioreactor.services['aerate'].run()
        time.sleep(6)
        self.bioreactor.services['calibrate_vessel'].reset()

    def prepare_to_aeration(self):
        self.bioreactor.services['pressure_release'].run()
        self.bioreactor.services['aerate'].run()

    def agitate_start(self, rpm):
        self.bioreactor.services['agitate'].change_configuration_parameter('agitate_setpoint', float(rpm))
        self.bioreactor.services['agitate'].run()

    def agitate_stop(self):
        self.bioreactor.services['agitate'].reset_state_to_idle()

    def reset_all_services(self):
        self.bioreactor.services['agitate'].reset_state_to_idle()
        self.bioreactor.services['aerate'].reset_state_to_idle()
        self.bioreactor.services['pressure_release'].reset_state_to_idle()
        self.bioreactor.services['calibrate_vessel'].reset_state_to_idle()
