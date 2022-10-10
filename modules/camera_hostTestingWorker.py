import socket
import threading
import time

class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # flag to pause thread
        self.paused = False
        self.timeToExit = False
        # Explicitly using Lock over RLock since the use of self.paused
        # break reentrancy anyway, and I believe using Lock could allow
        # one thread to pause the worker, while another resumes; haven't
        # checked if Condition imposes additional limitations that would
        # prevent that. In Python 2, use of Lock instead of RLock also
        # boosts performance.
        self.pause_cond = threading.Condition(threading.Lock())

    def run(self):
        while not self.timeToExit:
            with self.pause_cond:
                while self.paused:
                    self.pause_cond.wait()

                # thread should do the thing if
                # not paused
                print('do the thing')
            time.sleep(1)

    def pause(self):
        self.paused = True
        print("paused")
        # If in sleep, we acquire immediately, otherwise we wait for thread
        # to release condition. In race, worker will still see self.paused
        # and begin waiting until it's set back to False
        self.pause_cond.acquire()

    # should just resume the thread
    def resume(self):
        self.paused = False
        # Notify so thread will wake after lock released
        self.pause_cond.notify()
        # Now release the lock
        self.pause_cond.release()

    def stop(self):
        self.timeToExit = True

def runServer():
        print("Server Script Started")
        port = 8000  # Make sure it's within the > 1024 $$ <65535 range
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("localhost", port))
        s.listen(1)

        print("Waiting for incoming connection..")
        client_socket, adress = s.accept()
        print("Connection from: " + str(adress))

        myWorker=Worker()
        myWorker.start()
        while True:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break
            client_socket.send(data.encode('utf-8'))
            print('Recieved: ' + data)
            if data=="stop":
                #myWorker.
                client_socket.close()
                print("Client send Stop Command. Script will be terminated.")
                myWorker.stop()
                myWorker.join()
                exit(4)
            #exit(4)
            elif data=="resume":
                myWorker.resume()
            elif data=="pause":
                myWorker.pause()
        client_socket.close()

runServer()

