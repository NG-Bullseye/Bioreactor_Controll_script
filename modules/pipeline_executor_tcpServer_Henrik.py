import threading
import socket
from planteye_vision.inlet.generic_camera_inlet import GenericCameraInlet
from planteye_vision.inlet.static_data_inlet import StaticDataInlet
from planteye_vision.inlet.restapi_inlet import RestAPIDataInlet
from planteye_vision.shell.rest_api_shell import RestAPIShell
from planteye_vision.shell.tcp_Shell import PeriodicalLocalShell
from planteye_vision.processors.chunks_to_dict_processor import ChunksToDict
from planteye_vision.processors.encode_image_chunks_to_base_64_processor import EncodeImageChunksToBase64
from planteye_vision.processors.image_color_conversion_processor import ImageColorConversion
from planteye_vision.processors.image_crop_processor import ImageCrop
from planteye_vision.processors.image_resize_processor import ImageResize
from planteye_vision.processors.input_processor import InputProcessor
from planteye_vision.processors.save_on_disc_processor import SaveOnDiskProcessor
from planteye_vision.configuration.planteye_configuration import PlantEyeConfiguration
from planteye_vision.processors.data_processor import ConfigurableDataProcessor

import json
import logging
import time


class PipeLineExecutor:
    def __init__(self, config: PlantEyeConfiguration, pid: int):
        self.config = config
        self.shell = None
        self.inlets = []
        self.processors = []
        self.cfg_update_flag = False
        self.main_pid = pid

    def apply_configuration(self):
        logging.info('PIPELINE CONFIGURATION')
        if self.config.is_valid():
            self.configure_shell()
            self.configure_inlets()
            self.configure_processors()
        else:
            logging.error('Cannot apply configuration, configuration is invalid')

    def update_configuration(self):
        logging.info('CONFIGURATION UPDATE')
        self.cfg_update_flag = True
        self.configure_inlets()
        self.configure_processors()
        self.cfg_update_flag = False
        logging.info('New configuration applied')

    def configure_shell(self):
        logging.info('SHELL CONFIGURATION:')
        self.shell = []
        shell_config = self.config.get_shell_config()
        if shell_config.type == 'periodical_local':
            self.shell = PeriodicalLocalShell(shell_config, self.main_pid)
        elif shell_config.type == 'rest_api':
            self.shell = RestAPIShell(shell_config)
            self.shell.attach_planteye_configuration(self.config)
            self.shell.enable_configuration_update_via_restapi(self)
        else:
            self.shell = None
            logging.error(f'Unsupported shell type {shell_config.type}')
            return
        self.shell.attach_callback(self.single_execution)
        self.shell.apply_configuration()

        logging.info('Shell configured')

    def configure_inlets(self):
        self.inlets = []
        logging.info('INLETS CONFIGURATION:')
        inlet_configs = self.config.get_inlet_configs()
        inlets_obj = []
        for inlet_config in inlet_configs:
            if inlet_config.type == 'local_camera_cv2':
                inlet = GenericCameraInlet(inlet_config)
            elif inlet_config.type == 'baumer_camera_neoapi':
                from planteye_vision.inlet.baumer_camera_inlet import BaumerCameraInlet
                inlet = BaumerCameraInlet(inlet_config)
            elif inlet_config.type == 'static_variable':
                inlet = StaticDataInlet(inlet_config)
            elif inlet_config.type == 'opcua_variable':
                from planteye_vision.inlet.opcua_data_inlet import OPCUADataInlet
                inlet = OPCUADataInlet(inlet_config)
            elif inlet_config.type == 'restapi':
                inlet = RestAPIDataInlet(inlet_config)
            else:
                logging.error('Unsupported inlet type %s' % inlet_config.type)
                continue
            inlet.apply_configuration()
            inlets_obj.append(inlet)
            logging.info(f'Inlet: Name {inlet_config.name}, Type {inlet_config.type} added')

        self.inlets = inlets_obj
        logging.info('Inlets configured successfully')

    def configure_processors(self):
        self.processors = []
        logging.info('PROCESSORS CONFIGURATION:')
        processors_configs = self.config.get_processor_configs()
        processors_obj = []
        for processor_config in processors_configs:
            if processor_config.type == 'input':
                processor = InputProcessor(processor_config)
            elif processor_config.type == 'image_resize':
                processor = ImageResize(processor_config)
            elif processor_config.type == 'image_crop':
                processor = ImageCrop(processor_config)
            elif processor_config.type == 'color_conversion':
                processor = ImageColorConversion(processor_config)
            elif processor_config.type == 'tf_inference':
                from planteye_vision.processors.tf_model_inference_processor import TFModelInference
                processor = TFModelInference(processor_config)
            elif processor_config.type == 'pt_inference':
                from planteye_vision.processors.pt_model_inference_processor import PTModelInference
                processor = PTModelInference(processor_config)
            elif processor_config.type == 'save_on_disk':
                processor = SaveOnDiskProcessor(processor_config)
            else:
                logging.error('Unsupported inlet type %s' % processor_config.type)
                continue

            if isinstance(processor, ConfigurableDataProcessor):
                processor.apply_configuration()

            processors_obj.append(processor)
            logging.info(f'Processor: Name {processor.name}, Type {processor.type} added')

        self.processors = processors_obj
        logging.info('Processors configured successfully')

    def single_execution(self):
        logging.info('PIPELINE EXECUTION STEP')
        begin_time = time.time()
        logging.debug('Pipeline execution began')
        if self.cfg_update_flag:
            logging.error('Pipeline execution aborted, configuration ongoing')
            if isinstance(self.shell, RestAPIShell):
                return json.dumps(None)
            elif isinstance(self.shell, PeriodicalLocalShell):
                return None

        inlet_result = self.inlets_execute()
        processors_result = self.processors_execute(inlet_result)
        cleaned_processors_result = self.remove_duplicates(processors_result)
        combined_result = inlet_result + cleaned_processors_result

        if isinstance(self.shell, RestAPIShell):
            EncodeImageChunksToBase64().execute(combined_result)
            data_chunks_dict = ChunksToDict().execute(combined_result)
            result = json.dumps(data_chunks_dict)
        elif isinstance(self.shell, PeriodicalLocalShell):
            result = combined_result
        else:
            result = None

        end_time = time.time()
        exec_duration = end_time - begin_time
        logging.info(f'Pipeline execution finished (exec time {exec_duration:.3f} s)')

        return result

    def inlets_execute(self):
        data_chunks = []
        for inlet in self.inlets:
            data_chunks.extend(inlet.execute())
        return data_chunks

    def processors_execute(self, data_chunks):
        processing_result = data_chunks
        processor_results = []

        for processor in self.processors:

            if isinstance(processor, InputProcessor):
                processing_result = processor.execute(processing_result)
                if len(processing_result) == 0:
                    logging.error('Pipeline execution aborted, input processor returned nothing')
                    break
                continue

            elif isinstance(processor, SaveOnDiskProcessor):
                results_to_save = self.remove_duplicates(data_chunks + processor_results)
                processor.execute(results_to_save)
                continue

            processing_result = processor.execute(processing_result)
            if any([len(chunk.data) == 0 for chunk in processing_result]):
                logging.error(f'Pipeline execution aborted, processor {processor.name} returned nothing')
                break

            processor_results.extend(processing_result)
        return processor_results

    def remove_duplicates(self, data_chunks):
        return list(dict.fromkeys(data_chunks))

    def run(self):
        self.apply_configuration()
