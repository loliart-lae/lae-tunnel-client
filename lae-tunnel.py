# Lae Tunnel
# By Bing_Yanchi
# 主程序

from threading import Thread
from queue import Queue
from win10toast import ToastNotifier
import time, json, argparse, requests
import frpgo

# 通信部分    
q = Queue()
o = Queue()

# Windows 通知
toaster = ToastNotifier()

# 配置部分
get_tunnels_url = "http://lightart.top/api/v1/_tunnels"
get_project_url = "http://lightart.top/api/_projects"
get_server_url = "http://lightart.top/api/v1/_tunnels/create"

# 变量部分
project = {}
server = {}

def getUserInfo():
    r = requests.get(get_project_url + "?api_token={}".format(token))

    if (r.status_code != 200): return False

    result = json.loads(r.text)

    if (result['status'] == 0):
        print("[WARN] 请求出错, 或许是请求冷却或服务器故障")
        return False

    for line in result['data']:
        project[line['project']['id']] = line['project']['name']
    
    r = requests.get(get_server_url + "?api_token={}".format(token))

    if (r.status_code != 200): return False

    result = json.loads(r.text)

    if (result['status'] == 0):
        print("[WARN] 请求出错, 或许是请求冷却或服务器故障")
        return False
    
    for line in result['data']:
        server[line['id']] = line['name']


# 获取隧道列表
def printTunnel():
    #try:
        r = requests.get(get_tunnels_url + "?api_token={}".format(token))

        if (r.status_code == 200):
            # 正确获取
            result = json.loads(r.text)

            #print(result)
            if (result['status'] == 0):
                print("[WARN] 请求出错, 或许是请求冷却或服务器故障")
                return False
            
            table_header = "隧道 ID\t名称\t协议\t本地地址\t在线状态\t服务器 ID\t项目 ID\t最后在线"
            table_format = "{id}\t{name}\t{protocol}\t{local_address}\t{status}\t{server_id}\t{project_id}\t{ping}"
            
            print(table_header)

            for line in result['data']:
                print(table_format.format(id=line['id'], name=line['name'], protocol=line['protocol'], local_address=line['local_address'], status=line['status'], server_id=line['server_id'], project_id=line['project_id'], ping=line['ping']))
            return True
        else:
            # 验证失败
            print("错误代码: " , r.status_code)
            print(r.text)
            return False
    #except:
        # 本地错误
    #    print("[WARN] 请求出错, 或许是请求冷却或程序已过期")
    #    return False

# Debug 模式
Debug = False
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

        
        