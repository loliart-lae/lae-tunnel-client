# Lae Tunnel
# By Bing_Yanchi
# 主程序

from threading import Thread
#from win10toast import ToastNotifier
import time, json, argparse, requests, os, urllib3

# Windows 通知
#toaster = ToastNotifier()

# 配置部分
get_tunnels_url = "http://lightart.top/api/v1/_tunnels"
get_project_url = "http://lightart.top/api/_projects"
get_server_url = "http://lightart.top/api/v1/_tunnels/create"
get_config_url = " http://lightart.top/api/v1/_tunnels/"

# 变量部分
project = {}
server = {}
tunnel = {}
config = {}

# 调试模式
Debug = False

# 公用发送请求函数
def sendrequest(url, original):

    try:
        r = requests.get(url, verify=False)
    except requests.exceptions.SSLError:
        if (Debug):
            print("[DEBUG] 请求时发生的错误, 可能是 token 错误导致跳转 https")
        return False

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

# 获取项目与节点名称
def getUserInfo():
    
    result = sendrequest(get_project_url + "?api_token={}".format(token), False)

    if (result == False): return False
    if (result == "error"): return False

    for line in result:
        project[line['project']['id']] = line['project']['name']
    
    result = sendrequest(get_server_url + "?api_token={}".format(token), False)
    
    if (result == "error"): return False
    
    for line in result:
        server[line['id']] = line['name']

# 获取隧道列表
def printTunnel(is_arg):
    result = sendrequest(get_tunnels_url + "?api_token={}".format(token), False)

    if (result == False): return False
    if (result == "error"): return False
    
    if (not is_arg):
        table_format = "%-5s\t%-10s\t%-5s\t%-10s\t%-15s\t%-12s\t%-10s"
    
        print(table_format%("隧道 ID","名称","协议","本地地址","服务器","项目","最后在线"))

    for line in result:
        if (not is_arg):
            server_name = server[line['server_id']]
            project_name = project[line['project_id']]
            print(table_format%(line['id'],line['name'],line['protocol'],line['local_address'],server_name,project_name,line['ping']))
        tunnel[line['id']] = line['project_id']

    return True

# 下载配置文件
def get_config(id):
    result = sendrequest(get_config_url + str(id) + "?api_token={}".format(token), True)

    if (result == "error"): return False

    if (os.path.exists('config')) == False:
        os.mkdir('config')
    
    with open('config/lae-frp-{}.ini'.format(id), 'w', encoding='utf8') as f:
        f.write(result)
    
    return True

# 执行启动隧道
def runCmd(command):
    os.system(command)

# 删除配置文件
def removeFile(file):
    time.sleep(0.5)
    os.remove(file)

# 启动隧道
def runTunnel(tunnels):

    success = 0

    for tunnel_id in tunnels:
        try:
            tunnel_ID = int(tunnel_id)
        except ValueError:
            print("[WARN] 输入的隧道 ID 为非整数.")
            return False
        if (tunnel_ID in tunnel):
            # 下载配置文件
            if (get_config(tunnel_id)):
                # 启动程序
                command = 'api-frpclient.exe -c config/lae-frp-{}.ini'.format(tunnel_id)

                th_frpGo = Thread(target=runCmd, args=(command,))
                th_frpGo.setDaemon(True)
                th_frpGo.start()

                th_fileRemove = Thread(target=removeFile, args=('config/lae-frp-{}.ini'.format(tunnel_id),))
                th_fileRemove.setDaemon(True)
                th_fileRemove.start()

                success += 1
            else:
                print("[WARN] 获取隧道 ID 为 {} 的配置文件失败, 或许是网络问题或 token 过期.".format(tunnel_id))
    
    if (success == 0): return False
    else: return True

# 向用户获取 Token
def getToken(is_arg):
    global token
    if (not is_arg):
        token = input("[INFO] 输入你的 Token: ")

    getUserInfo()

    if (printTunnel(is_arg)):
        return True
    else:
        if (is_arg):
            print("[ERROR] Token 验证失败.")
        else:
            print("[WARN] Token 验证失败, 请重试...")
        return False

# 向用户获取 隧道 ID
def getTunnelID(is_arg):
    global arg_tunnel
    if (not is_arg):
        arg_tunnel = input("[INFO] 输入你要连接的隧道 ID (直接回车将连接所有隧道, 使用英文逗号分割可连接多个): ")
        # 空输入
        if (arg_tunnel == ""):
            project_format = ", {id} - {name}"

            project_str = "[INFO] 回车 - 所有项目"

            for project_id in project.keys():
                project_str += project_format.format(id=project_id, name=project[project_id])

            print(project_str)

            while (1):
                choose_project = input("[INFO] 选择你要启动哪个或哪些的项目中的所有隧道: ")

                if (choose_project == ""):
                    arg_tunnel = list(tunnel.keys())
                    break
                else:
                    # TODO 分隔符
                    try:
                        choose_project = int(choose_project)
                    except ValueError:
                        print("[WARN] 输入非整数, 请重新输入...")
                        continue
                        
                    # 判断是否在项目列表
                    if choose_project in project.keys():
                        arg_tunnel = []
                        for tunnel_id in tunnel.keys():
                            if tunnel[tunnel_id] == choose_project:
                                arg_tunnel.append(tunnel_id)

                        if (len(arg_tunnel) == 0):
                            print("[WARN] 该项目中没有隧道, 请重新输入...")
                            continue
                        else:
                            break
                    else:
                        print("[WARN] 输入的值非允许值, 请重新输入...")
                        continue
        else:
            arg_tunnel = arg_tunnel.split(',')

    if(runTunnel(arg_tunnel)):
        return True
    else:
        if (is_arg):
            print("[ERROR] 你提供的隧道 ID 均不存在.")
        else:
            print("[WARN] 所有输入的隧道均不存在, 请重新输入...")

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
    parser.add_argument('-a', '--token', help='user token')
    parser.add_argument('-t', '--tunnel', help='tunnel ID (Use , split)')
    args = parser.parse_args()

    token = args.token
    arg_tunnel = args.tunnel
    if (arg_tunnel != None):
        arg_tunnel = arg_tunnel.split(',')

    # 最默认的模式
    if (args.token == None and args.tunnel == None):

        while (1):
            if (getToken(False)): break
        
        while(1):
            if (getTunnelID(False)): break
            
    # 仅提供了 token
    elif (args.token != None and args.tunnel == None):
        print("[INFO] 你已使用参数启动, 正在获取隧道信息...")

        if (getToken(True) == False): 
            os._exit(0)
        while(1):
            if (getTunnelID(False)): break
    # 都提供了
    else:
        print("[INFO] 你已使用参数启动, 正在直接启动隧道...")

        if (getToken(True) == False):
            os._exit(0)

        if (getTunnelID(True) == False):
            os._exit(0)
    
    # 阻塞防止关闭
    while(1):
        continue