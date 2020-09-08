#coding='utf-8'
import requests
import time
import hashlib
import json
import pandas as pd

import pdb

url = "https://www.educoder.net/api/tasks/%s/get_answer_info.json?randomcode=%s&client_key=%s"
open_key = "79e33abd4b6588941ab7622aed1e67e8"
headers = {
    "Cookie":"autologin_trustie=84f63d2f9b388c2e1b9417fb0b35d5996799ebc2; _educoder_session=a5aec033be5e6a655e1fc77a1c53c3b9"
}
task_url = "https://www.educoder.net/api/shixuns/%s/shixun_exec.json?randomcode=%s&client_key=%s"
myshixuns = "https://www.educoder.net/api/tasks/%s.json?randomcode=%s&client_key=%s"
challenges = "https://www.educoder.net/api/myshixuns/%s/challenges.json?randomcode=%s&client_key=%s"


def parser_data(shixun_pagecontent, session, crawl_data):
    shixun_pagecontent_json = json.loads(shixun_pagecontent)
    for shixun in shixun_pagecontent_json["shixuns"]:
        shixun_id = shixun["id"]
        shixun_name = shixun["name"]

        identifier = shixun["identifier"]
        randomcode = str(time.time()).split('.')[0]
        res = ''
        clientkey = hashlib.md5((open_key + randomcode).encode()).hexdigest()

        print("clientkey: {}".format(clientkey))
        try:
            taskjson = json.loads(session.get(task_url % (identifier, randomcode, clientkey), headers=headers).content)
        except Exception as e:
            print(e)
            continue
        if 'game_identifier' not in taskjson:
            continue
        game_identifier = taskjson["game_identifier"]

        try:
            myshixun = session.get(myshixuns % (game_identifier, randomcode, clientkey), headers=headers).content
        except Exception as e:
            print(e)
            continue
        myshixuns_md5 = json.loads(myshixun)["myshixun"]["identifier"]

        try:
            tasks_md5 = session.get(challenges % (myshixuns_md5, randomcode, clientkey), headers=headers).content
        except Exception as e:
            print(e)
            continue
        tasks_md5_json = json.loads(tasks_md5)
        for task in tasks_md5_json:
            challenge_identifier = task["identifier"]
            challenge_name = task["name"]
            print(task["position"])
            position = str(task["position"])
            
            try:
                res = session.get(url % (task["identifier"], randomcode, clientkey), headers=headers).content
            except Exception as e:
                print(e)
            
            print("res: {}".format(res))
            res_json = json.loads(res)
            if len(res_json["message"]) != 0:
                answer_id = res_json["message"][0]["answer_id"]
                answer_content = res_json["message"][0]["answer_contents"]
            else:
                answer_id = ''
                answer_content = ''
            crawl_data.append([shixun_id, shixun_name, position, challenge_identifier, challenge_name, answer_id, answer_content])




def get_data():
    session = requests.Session()
    crawl_data = []
    name = ["shixun_id", "shixun_name", "position", "challenge_id", "challenge_name", "answer_id", "answer_contents"]

    for i in range(1, 18):
        shixun_pagecontent = session.get("https://www.educoder.net/api/shixuns.json?randomcode=1579257227&client_key=5004958011025f338b9f9b697e8bcbdd&order_by=new&tag_level=3&tag_id=160&page=" + str(i) + "&limit=16&keyword=&status=0&diff=0&sort=desc", headers=headers).content
        parser_data(shixun_pagecontent, session, crawl_data)
    shixun_pagecontent = session.get(
        "https://www.educoder.net/api/shixuns.json?randomcode=1579257227&client_key=5004958011025f338b9f9b697e8bcbdd&order_by=new&tag_level=3&tag_id=161&page=1" 
        "&limit=500&keyword=&status=0&diff=0&sort=desc", headers=headers).content
    parser_data(shixun_pagecontent, session, crawl_data)

    test = pd.DataFrame(columns=name, data=crawl_data)
    pdb.set_trace()
    test.to_csv("./data/standardcode.csv", encoding='utf8')


if __name__ == '__main__':
    get_data()
