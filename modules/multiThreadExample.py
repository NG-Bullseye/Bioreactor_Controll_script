import threading
import time


class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        # flag to pause thread
        self.paused = False
        # Explicitly using Lock over RLock since the use of self.paused
        # break reentrancy anyway, and I believe using Lock could allow
        # one thread to pause the worker, while another resumes; haven't
        # checked if Condition imposes additional limitations that would
        # prevent that. In Python 2, use of Lock instead of RLock also
        # boosts performance.
        self.pause_cond = threading.Condition(threading.Lock())

    def run(self):
        while True:
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
    def exitWorker(self):
        exit(5)
    def resume(self):
        self.paused = False
        # Notify so thread will wake after lock released
        self.pause_cond.notify()
        # Now release the lock
        self.pause_cond.release()



def workerMinimal():
    exit(4)
def runMinimal():
    thread = threading.Thread(target=workerMinimal)
    thread.start()
    input("Input3: ")
    exit(3)
