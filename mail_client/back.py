import urllib.request as url
from time import strftime
import random
import json
import sys

message = sys.argv[1] if len(sys.argv) > 1 else "Eliezer, "

URL = "http://127.0.0.1:5000/send"
URL_CHECK = "http://127.0.0.1:5000/status"
DATA = json.dumps({"recipient": "@_eliezerkenya_", "message": f"*{strftime('%Y-%m-%d %H:%M:%S')}* Backup Logs, \n{message}"}).encode("utf-8")

def check_endpoint():
    try:
        val = url.Request(URL_CHECK, method="GET")
        with url.urlopen(val) as resp:
            if json.loads(resp.read().decode())["success"]:
                return True
            else:
                return False
    except Exception as e:
        print(f"\nException: {e}\n")
        return False

def run():
    if check_endpoint():
        req = url.Request(URL, data=DATA, headers={"Content-Type": "application/json", "X-API-Key": "@newlycreated-wha-bot"}, method="POST")
        with url.urlopen(req) as resp:
            if resp.status == 200:
                print("\nMessage sent HTTP\\ ", resp.status)
        print(f"Success: {strftime('%Y-%m-%d %H:%M:%S')}\n")
    else:
        print("\nFailed!\n")

if __name__=="__main__":
    run()
