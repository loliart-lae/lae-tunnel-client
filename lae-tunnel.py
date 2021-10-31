# Lae Tunnel
# By Bing_Yanchi
# 主程序

from threading import Thread
#from win10toast import ToastNotifier
import time, json, argparse, requests, os, yaml

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

# 语言
language = {}
language_code = "zh_cn"

# 获取配置文件
def read_config():
    config = {}
    with open('config.yml', 'r', encoding="utf-8") as f:
        config = yaml.load(f, Loader= yaml.SafeLoader)
    # 读取
    global Debug, language_code, get_tunnels_url, get_project_url, get_server_url, get_config_url
    Debug = config.get('debug')
    language_code = config.get('language')
    get_tunnels_url = config.get('api.get_tunnels')
    get_project_url = config.get('api.get_project')
    get_server_url = config.get('api.get_server')
    get_config_url = config.get('api.get_config')

# 读取语言文件
def read_language(Language):
    global language, language_code
    with open(Language, 'r', encoding="utf-8") as f:
        language = yaml.load(f, Loader = yaml.SafeLoader)

# 公用发送请求函数
def sendrequest(url, original):

    try:
        r = requests.get(url, verify=False)
    except requests.exceptions.SSLError:
        if (Debug):
            print(language['debug'] + language['ssl_error'])
        return False

    for i in range(0,3):

        if (r.status_code != 200):
            if (Debug):
                print(language['debug'] + language['status_code_error'].format(code=str(r.status_code), url=url))
            continue

        if (original == True):
            return r.text

        result = json.loads(r.text)

        if (result['status'] == 0):
            print(language['warn'] + language['status_error'])
            return "error"
        
        return result['data']

    if (Debug):
        print(language['debug'] + language['fail_request'])
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
    
        print(table_format%(language['tunnel_id'],language['tunnel_name'],language['tunnel_protocol'],language['tunnel_local_address'],language['tunnel_server'],language['tunnel_project'],language['tunnel_ping']))

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
            print(language['warn'] + language['tunnel_input_value_warn'])
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
                print(language['warn'] + language['tunnel_get_config_warn'].format(tunnel_id))
    
    if (success == 0): return False
    else: return True

# 向用户获取 Token
def getToken(is_arg):
    global token
    if (not is_arg):
        token = input(language['info'] + language['token_input'])
        if (token == ""):
            print(language['warn'] + language['token_null'])
            return False

    getUserInfo()

    if (printTunnel(is_arg)):
        return True
    else:
        if (is_arg):
            print(language['error'] + language['token_fail'])
        else:
            print(language['warn'] + language['token_warn'])
        return False

# 向用户获取 隧道 ID
def getTunnelID(is_arg):
    global arg_tunnel
    if (not is_arg):
        arg_tunnel = input(language['info'] + language['tunnel_input'])
        # 空输入
        if (arg_tunnel == ""):
            project_format = language['project_format']

            project_str = language['info'] + language['project_str']

            for project_id in project.keys():
                project_str += project_format.format(id=project_id, name=project[project_id])

            print(project_str)

            while (1):
                if (arg_project == None):
                    choose_project = input(language['info'] + language['tunnel_project_input'])
                else:
                    choose_project = arg_project

                if (choose_project == ""):
                    arg_tunnel = list(tunnel.keys())
                    break
                else:
                    try:
                        choose_project = choose_project.split(",")
                        
                        for i in range(len(choose_project)):
                            choose_project[i] = int(choose_project[i])
                    except ValueError:
                        if (args.project == None):
                            print(language['warn'] + language['tunnel_project_id_warn'])
                            continue
                        else:
                            print(language['error'] + language['tunnel_project_id_fail'])
                            break
                        
                    
                    arg_tunnel = []
                    for project_num in choose_project:
                        # 判断是否在项目列表
                        if project_num in project.keys():
                            
                            for tunnel_id in tunnel.keys():
                                if tunnel[tunnel_id] == project_num:
                                    arg_tunnel.append(tunnel_id)
                        else:
                            print(language['warn'] + language['tunnel_project_id_pass'].format(str=project_num))

                    if (len(arg_tunnel) == 0):
                        if (args.project == None):
                            print(language['warn'] + language['tunnel_project_no_tunnel_warn'])
                            continue
                        else:
                            print(language['error'] + language['tunnel_project_no_tunnel_fail'])
                            break
                    else:
                        break
                    
        else:
            arg_tunnel = arg_tunnel.split(',')

    if(runTunnel(arg_tunnel)):
        return True
    else:
        if (is_arg):
            print(language['error'] + language['tunnel_not_found_fail'])
        else:
            print(language['warn'] + language['tunnel_not_found_warn'])

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
    # 读取配置文件
    read_config()
    read_language("language/{}.yml".format(language_code))

    # 检查参数
    parser = argparse.ArgumentParser(description=language['arg_description'])
    parser.add_argument('-a', '--token', help=language['arg_token'])
    parser.add_argument('-t', '--tunnel', help=language['arg_tunnel'])
    parser.add_argument('-p', '--project', help=language['arg_project'])
    args = parser.parse_args()

    token = args.token
    arg_tunnel = args.tunnel
    arg_project = args.project
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
        print(language['info'] + language['has_token_arg'])

        if (getToken(True) == False): 
            os._exit(0)
        while(1):
            if (getTunnelID(False)): break
    # 都提供了
    else:
        print(language['info'] + language['has_tunnel_arg'])

        if (getToken(True) == False):
            os._exit(0)

        if (getTunnelID(True) == False):
            os._exit(0)
    
    # 阻塞防止关闭
    while(1):
        pass