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

# 变量部分
project = {}
server = {}

# 调试模式
Debug = False

def sendrequest(url):

    r = requests.get(url)

    for i in range(0,3):

        if (r.status_code != 200):
            if (Debug):
                print("[DEBUG] 有一条请求状态码错误: {} - {}".format(str(r.status_code), url))
            continue

        result = json.loads(r.text)

        if (result['status'] == 0):
            print("[WARN] 请求出错, 或许是请求冷却或服务器故障")
            return "error"
        
        return result['data']

    if (Debug):
        print("[DEBUG] 多次请求失败, 已放弃")
    return "error"

def getUserInfo():
    
    result = sendrequest(get_project_url + "?api_token={}".format(token))

    if (result == "error"): return False

    for line in result:
        project[line['project']['id']] = line['project']['name']
    
    result = sendrequest(get_server_url + "?api_token={}".format(token))
    
    if (result == "error"): return False
    
    for line in result:
        server[line['id']] = line['name']


# 获取隧道列表
def printTunnel():
    result = sendrequest(get_tunnels_url + "?api_token={}".format(token))

    if (result == "error"): return False
            
    table_header = "隧道 ID\t名称\t协议\t本地地址\t在线状态\t服务器\t项目\t最后在线"
    table_format = "{id}\t{name}\t{protocol}\t{local_address}\t{status}\t{server_id}\t{project_id}\t{ping}"
            
    print(table_header)

    for line in result:
        if (line['status'] == 1): status_name = "在线"
        else: status_name = "离线"
        server_name = server[line['server_id']]
        project_name = project[line['project_id']]
        print(table_format.format(id=line['id'], name=line['name'], protocol=line['protocol'], local_address=line['local_address'], status=status_name, server_id=server_name, project_id=project_name, ping=line['ping']))
    return True

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
    tunnel = args.tunnel

    # 最默认的模式
    if (token == None and tunnel == None):

        while (1):

            token = input("[INFO] 输入你的 Token: ")

            getUserInfo()

            print(project)
            print(server)

            if (printTunnel()):
                break
            else:
                print("[WARN] Token 验证失败, 请重试...")
        
        while(1):

            tunnel = input("[INFO] 输入你要连接的隧道: ")

        
        