from planteye_vision.pipeline_execution.pipeline_executor_tcpServer import PipeLineExecutor
from planteye_vision.configuration.planteye_configuration import PlantEyeConfiguration
from yaml import safe_load
import logging
import argparse
import sys


def read_config_file(path_to_cfg):
    logging.info(f'Configuration is read from the file {path_to_cfg}')
    with open(path_to_cfg) as config_file:
        config_dict = safe_load(config_file)
    return config_dict


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PlantEye: Smart Camera')
    parser.add_argument('--cfg',
                        help="Path to configuration file",
                        metavar='config',
                        type=str,
                        required=False)
    args = parser.parse_args(sys.argv[1:])
    print(args)

    logging.basicConfig(format='%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

    path_to_cfg = args.cfg
    if path_to_cfg is None:
        path_to_cfg = 'config_opencv2_restapi_minimal.yaml'

    config_dict = read_config_file(path_to_cfg)

    config = PlantEyeConfiguration()
    config.read(config_dict)
    PipeLineExecutor(config).run()
