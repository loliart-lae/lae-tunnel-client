# Lae Tunnel
# By Bing_Yanchi

from threading import Thread
from datetime import datetime, timedelta
import time, json, argparse, requests, os, yaml

# 配置部分
get_tunnels_url = "http://lightart.top/api/v1/_tunnels"
get_project_url = "http://lightart.top/api/_projects"
get_server_url = "http://lightart.top/api/v1/_tunnels/create"
get_config_url = " http://lightart.top/api/v1/_tunnels/"

# frpc 命令
frpc_command = "api-frpclient.exe -c {file}"
frpc_config = "config/lae-frp-{id}.ini"

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
    global Debug, language_code, get_tunnels_url, get_project_url, get_server_url, get_config_url, frpc_command, frpc_config
    Debug = config['debug']
    language_code = config['language']
    get_tunnels_url = config['api']['get_tunnels']
    get_project_url = config['api']['get_project']
    get_server_url = config['api']['get_server']
    get_config_url = config['api']['get_config']
    frpc_command = config['frpc_command']
    frpc_config = config['frpc_config']

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

    for i in range(0,5):

        if (r.status_code != 200):
            if (Debug):
                print(language['debug'] + language['status_code_error'].format(code=str(r.status_code), url=url))
            time.sleep(0.2)
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

        print()

        table_format = "%-5s\t%-10s\t%-5s\t%-10s\t%-15s\t%-12s\t%-5s\t%-10s"
    
        print(table_format%(language['tunnel_id'],language['tunnel_name'],language['tunnel_protocol'],language['tunnel_local_address'],language['tunnel_server'],language['tunnel_project'],language['tunnel_project_id'],language['tunnel_ping']))

        for line in result:
            server_name = server[line['server_id']]
            project_name = project[line['project_id']]
            # 最后在线时间
            if (line['ping'] != None):
                ping_time = datetime.strptime(line['ping'], '%Y-%m-%d %H:%M:%S')
                now_time = datetime.now()

                if (now_time - ping_time <= timedelta(seconds=70)):
                    line['ping'] = "\033[1;33;1m{time}\033[0m".format(time=line['ping'])

            print(table_format%(line['id'],line['name'],line['protocol'],line['local_address'],server_name,project_name,"p" + str(line['project_id']),line['ping']))
        
        print()

    for line in result:            
        tunnel[line['id']] = line['project_id']

    return True

# 下载配置文件
def get_config(id):

    result = sendrequest(get_config_url + str(id) + "?api_token={}".format(token), True)

    if (result == "error"): return False

    if (os.path.exists('config')) == False:
        os.mkdir('config')
    
    with open(frpc_config.format(id=id), 'w', encoding='utf-8') as f:
        f.write(result)
    
    return True

# 执行启动隧道
def runCmd(command):
    os.system(command)

# 启动隧道
def runTunnel(tunnels):

    success = 0

    for tunnel_id in tunnels:
        if (tunnel_id in tunnel):
            if (args.latest and os.path.exists(frpc_config.format(id=id))):
                success += 1
            else:
                # 下载配置文件
                if (get_config(tunnel_id)):
                    success += 1
                    # 间隔
                    time.sleep(0.3)
                else:
                    print(language['warn'] + language['tunnel_get_config_warn'].format(id=tunnel_id))
                    continue
                
            # 启动程序
            command = frpc_command.format(file=frpc_config.format(id=tunnel_id))

            th_frpGo = Thread(target=runCmd, args=(command,))
            th_frpGo.setDaemon(True)
            th_frpGo.start()
            time.sleep(0.3)
    
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

    if (printTunnel(args.tunnel != None)):
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

    tunnel_list = []

    # 判断是否为空
    if (arg_tunnel == ''):
        tunnel_list = list(tunnel_list.keys())
    else:
        # 拆分输入
        arg_tunnel = arg_tunnel.split(',')

        for key in arg_tunnel:
            # 如果为项目编号
            if (key.startswith('p')):
                # 检查输入项目是否为数字
                try:
                    key = key.lstrip('p')

                    key = int(key)
                except ValueError:
                    print(language['warn'] + language['tunnel_project_id_warn'])
                    continue

                # 判断是否在项目列表
                if key in project.keys():
                    # 循环添加其中的隧道
                    for tunnel_id in tunnel.keys():
                        # 指定项目中的隧道, 并且未添加的
                        if tunnel[tunnel_id] == key and tunnel_id not in tunnel_list:
                            tunnel_list.append(tunnel_id)
                # 不存在时通知提醒
                else:
                    print(language['warn'] + language['tunnel_project_id_pass'].format('p' + str(id=key)))
            # 为普通隧道 ID
            else:
                # 判断输入是否为整数
                try:
                    key = int(key)
                except ValueError:
                    print(language['warn'] + language['tunnel_input_value_warn'])
                    continue

                if key in tunnel:
                    if key not in tunnel_list:
                        tunnel_list.append(key)
                # 不存在隧道提醒
                else:
                    print(language['warn'] + language['tunnel_input_not_found'].format(id=key))

    if(runTunnel(tunnel_list)):
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
    parser.add_argument('--token', help=language['arg_token'])
    parser.add_argument('-t', '--tunnel', help=language['arg_tunnel'])
    parser.add_argument('--lang', help=language['arg_lang'])
    parser.add_argument('--latest', help=language['arg_latest'], action='store_true')
    args = parser.parse_args()

    read_language("language/{}.yml".format(language_code))

    token = args.token
    arg_tunnel = args.tunnel

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