# Lae Tunnel
# By Bing_Yanchi
# 主程序

from threading import Thread
from queue import Queue
#from win10toast import ToastNotifier
import time, json, argparse, requests
import frpgo

# 通信部分    
q = Queue()
o = Queue()

# Windows 通知
#toaster = ToastNotifier()

# 配置部分
get_tunnels_url = "http://lightart.top/api/v1/_tunnels"
get_project_url = "http://lightart.top/api/_projects"
get_server_url = "http://lightart.top/api/v1/_tunnels/create"
get_config_url = " https://lightart.top/api/v1/_tunnels/"

# 变量部分
project = {}
server = {}
tunnel = {}
config = {}

# 调试模式
Debug = False

def sendrequest(url, original):

    r = requests.get(url)

    for i in range(0,3):

        if (r.status_code != 200):
            if (Debug):
                print("[DEBUG] 有一条请求状态码错误: {} - {}".format(str(r.status_code), url))
            continue

        if (original == True):
            return r.text

        result = json.loads(r.text)

        if (result['status'] == 0):
            print("[WARN] 请求出错, 或许是请求冷却或服务器故障")
            return "error"
        
        return result['data']

    if (Debug):
        print("[DEBUG] 多次请求失败, 已放弃")
    return "error"

def getUserInfo():
    
    result = sendrequest(get_project_url + "?api_token={}".format(token), False)

    if (result == "error"): return False

    for line in result:
        project[line['project']['id']] = line['project']['name']
    
    result = sendrequest(get_server_url + "?api_token={}".format(token), False)
    
    if (result == "error"): return False
    
    for line in result:
        server[line['id']] = line['name']


# 获取隧道列表
def printTunnel():
    result = sendrequest(get_tunnels_url + "?api_token={}".format(token), False)

    if (result == "error"): return False
    
    table_format = "%-5s\t%-10s\t%-5s\t%-10s\t%-15s\t%-12s\t%-10s"
            
    print(table_format%("隧道 ID","名称","协议","本地地址","服务器","项目","最后在线"))

    for line in result:
        server_name = server[line['server_id']]
        project_name = project[line['project_id']]
        print(table_format%(line['id'],line['name'],line['protocol'],line['local_address'],server_name,project_name,line['ping']))
        tunnel[line['id']] = line['project_id']

    return True

# 下载配置文件
def get_config(id):
    result = sendrequest(get_config_url + id + "?api_token={}".format(token), True)

    if (result == "error"): return False



# 启动隧道
def runTunnel(tunnels):

    success = 0

    for tunnel_id in tunnels:
        if (tunnel_id in tunnel.keys()):

            success += 1
    
    if (success == 0): return False
    else: return True


# Debug 模式
if (not Debug):
    print("========================================================================================================")
    print("")
    print("████████╗██╗   ██╗███╗   ██╗███╗   ██╗███████╗██╗          ██████╗██╗     ██╗███████╗███╗   ██╗████████╗")
    print("╚══██╔══╝██║   ██║████╗  ██║████╗  ██║██╔════╝██║         ██╔════╝██║     ██║██╔════╝████╗  ██║╚══██╔══╝")
    print("   ██║   ██║   ██║██╔██╗ ██║██╔██╗ ██║█████╗  ██║         ██║     ██║     ██║█████╗  ██╔██╗ ██║   ██║   ")
    print("   ██║   ██║   ██║██║╚██╗██║██║╚██╗██║██╔══╝  ██║         ██║     ██║     ██║██╔══╝  ██║╚██╗██║   ██║   ")
    print("   ██║   ╚██████╔╝██║ ╚████║██║ ╚████║███████╗███████╗    ╚██████╗███████╗██║███████╗██║ ╚████║   ██║   ")
    print("   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚══════╝     ╚═════╝╚══════╝╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ")
    print("                                                                                                        ")
    print("========================================================================================================")
    print("")

if __name__ == "__main__":
    # 检查参数
    parser = argparse.ArgumentParser(description='Light App Engine Tunnel Client.')
    parser.add_argument('-a', '--token', help='User Token')
    parser.add_argument('-t', '--tunnel', help='Tunnel ID (Use , split)')
    args = parser.parse_args()

    token = args.token
    arg_tunnel = args.tunnel.split(',')

    # 最默认的模式
    if (token == None and arg_tunnel == None):

        while (1):

            token = input("[INFO] 输入你的 Token: ")

            getUserInfo()

            if (printTunnel()):
                break
            else:
                print("[WARN] Token 验证失败, 请重试...")
        
        while(1):

            arg_tunnel = input("[INFO] 输入你要连接的隧道 ID (直接回车将连接所有隧道): ").split(',')

            if(runTunnel(arg_tunnel)):
                break
            else:
                print("[WARN] 所有输入的隧道均不存在, 请重新输入...")
        



