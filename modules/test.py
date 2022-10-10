import logging
import threading
from time import time, sleep
from planteye_vision.shell.shell import Shell
from planteye_vision.configuration.shell_configuration import PeriodicalLocalShellConfiguration
import socket

stop_flag = False
paused = False

class PeriodicalLocalShell(Shell):
    """
    This class describes a local shell that requests data periodically
    """
    def __init__(self, config: PeriodicalLocalShellConfiguration):
        self.config = config
        self.time_scheduler = None
        self.callback = None
        self.tcpServer=None

    def apply_configuration(self):
        self.time_scheduler = TimeScheduler(self.config.parameters['time_interval'], self.execution_step)
        self.time_scheduler.start()
        self.tcpServer = threading.Thread(target=self.runServer)
        self.tcpServer.start()

    def attach_callback(self, callback):
        self.callback = callback

    def execution_step(self):
        self.callback()

    def runServer(self):
        global paused
        global stop_flag
        print("Server Script Started")
        port = 8000  # Make sure it's within the > 1024 $$ <65535 range
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", port))
        s.listen(1)

        print("Waiting for incoming connection..")
        client_socket, adress = s.accept()
        print("Connection from: " + str(adress))

        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            client_socket.send(data.encode('utf-8'))
            print('Recieved: ' + data)
            if data == "stop":
                client_socket.close()
                print("Client send Stop Command. Script will be terminated.")
                stop_flag = True
                # exit(4)
            elif data == "resume":
                paused=False
            elif data == "pause":
                paused = True
        client_socket.close()


class TimeScheduler:
    def __init__(self, time_interval: float, executed_function):
        self.time_interval = time_interval
        self.executed_function = executed_function
        self.thread = None
        global stop_flag
        stop_flag=False
        global paused
        paused=False

    def start(self):
        global stop_flag
        stop_flag=False
        self.thread = threading.Thread(target=self.executable, args=[])
        self.thread.start()

    def stop(self):
        global stop_flag
        stop_flag = True

    def pause(self):
        global paused
        paused = True

    def resume(self):
        global paused
        paused = False

    def executable(self):
        expected_step_end = time() - self.time_interval / 1000.0
        while not stop_flag:
            while paused:
                pass
            logging.debug('Shell execution step began')
            step_begin = time()
            expected_step_end = expected_step_end + self.time_interval / 1000.0
            if step_begin > expected_step_end:
                logging.error('Shell execution step skipped (consider increasing interval)')
                continue
            self.executed_function()
            if time() > expected_step_end:
                warn_msg = f'Shell execution step took longer than given time interval ({self.time_interval/1000.0} s)'
                logging.warning(warn_msg)
            else:
                sleep(max(expected_step_end-time(), 0))







