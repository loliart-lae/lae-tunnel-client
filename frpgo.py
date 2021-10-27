# FrpGo
# By Bing_Yanchi
from threading import Thread
import subprocess,time,psutil,asyncio

class GoGo:

    def __init__(self, shell, out_q, o):

        self.p = subprocess.Popen(shell, shell=True, stdout=subprocess.PIPE)

        self.o = o

        self.send = public_channel_client(out_q)

        self.th_exit = Thread(target=self.run_q)
        self.th_exit.setDaemon(True)
        self.th_exit.start()

        loop.run_until_complete(self.get_pid("api-frpclient.exe"))

        for line in iter(self.p.stdout.readline, b''):
            line = line.strip().decode("GB2312")
            self.send.run(line)
            time.sleep(0.2)
    
    async def get_pid(self, name):

        await asyncio.sleep(0.5)

        create_time = 0
        tid = 0

        for proc in psutil.process_iter():
            if(proc.name() == name):
                if (proc.create_time() > create_time):
                    tid = proc.pid
                    create_time = proc.create_time()
        self.frpID = tid
    
    def run_q(self):
        while True:
            get_data = self.o.get()
            print("[DEBUG - 通信 - FrpGo] " + get_data)
            if (get_data == "exit"):

                self.p.kill()
                try:
                    p = psutil.Process(self.frpID)
                    p.terminate()

                    self.send.run("[QuickTCP] Cleared successfully.")
                except:
                    print("[DEBUG - 警告 - FrpGo] 尝试杀死进程 {} 失败".format(self.frpID))

def GO(shell, out_q, o):
    GoGo(shell, out_q, o)

# 异步
loop = asyncio.get_event_loop()

# 通信部分
class public_channel_client(object):
    def __init__(self, out_q):
        self.q = out_q

    def run(self, data):
        self.q.put(data)