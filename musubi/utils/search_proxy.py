import requests
from tqdm import tqdm
import re
from pathlib import Path
import os
import json
import socket


hostname = socket.gethostname()
IPADDR = socket.gethostbyname(hostname)

 
def search_https_proxy(
    save_dir: str = "config"
):
    if not os.path.isdir(save_dir):
        os.mkdir(save_dir)

    save_path = Path(save_dir) / "proxies.json"
    
    response = requests.get("https://free-proxy-list.net/anonymous-proxy.html")
    proxy_ips = re.findall('\d+\.\d+\.\d+\.\d+:\d+', response.text)

    for ip in tqdm(proxy_ips):
        try:
            res = requests.get('https://api.ipify.org', proxies={"https": ip}, timeout=3).text
            if res != IPADDR:
                with open(save_path, "a+", encoding="utf-8") as file:
                    file.write(json.dumps({"https_proxy_ip": ip}, ensure_ascii=False) + "\n")
        except:
            pass