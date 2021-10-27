# Lae Tunnel
# By Bing_Yanchi
# 主程序

from threading import Thread
from queue import Queue
from win10toast import ToastNotifier
import time, json, argparse
import frpgo

# 通信部分    
q = Queue()
o = Queue()

# Windows 通知
toaster = ToastNotifier()

# Debug 模式
Debug = False
if (Debug):
    print("========================================================================================================")
    print("")
    print("████████╗██╗   ██╗███╗   ██╗███╗   ██╗███████╗██╗          ██████╗██╗     ██╗███████╗███╗   ██╗████████╗")
    print("╚══██╔══╝██║   ██║████╗  ██║████╗  ██║██╔════╝██║         ██╔════╝██║     ██║██╔════╝████╗  ██║╚══██╔══╝")
    print("   ██║   ██║   ██║██╔██╗ ██║██╔██╗ ██║█████╗  ██║         ██║     ██║     ██║█████╗  ██╔██╗ ██║   ██║   ")
    print("   ██║   ██║   ██║██║╚██╗██║██║╚██╗██║██╔══╝  ██║         ██║     ██║     ██║██╔══╝  ██║╚██╗██║   ██║   ")
    print("   ██║   ╚██████╔╝██║ ╚████║██║ ╚████║███████╗███████╗    ╚██████╗███████╗██║███████╗██║ ╚████║   ██║   ")
    print("   ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚══════╝     ╚═════╝╚══════╝╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ")
    print("                                                                                                        ")
    print("[DEBUG] 嘿，你目前处于调试模式，更多记录将会展示")
    print("========================================================================================================")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description='Light App Engine Tunnel Client.')
    parser.add_argument('-a', '--token', help='User Token')
    parser.add_argument('-t', '--tunnel', help='Tunnel ID (Use , split)', type=int)
    args = parser.parse_args()
    ip = args.address or '0.0.0.0'
    port = args.port or 8080

    print(ip, port)
