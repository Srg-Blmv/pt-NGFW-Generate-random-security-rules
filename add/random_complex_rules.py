import requests
import random
import ipaddress
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)




global_gr_id = ""
cookies = ""
headers = {"Content-Type": "application/json"}
payload = {}



app_list = [
# до Версии 1.10 были проблемы что не все app могут пропушиться.  список исключений сюда, или список необходимых приложений
# в функции get_app  раскоментировать строчку ( if item["name"] not in app_list ) и сделать Tab на двух следующих  строках 
]


def auth():
    global global_gr_id, cookies
    
    url = f"https://{mgmt_ip}/api/v2/Login"
    payload = {
        "login": mgmt_login,
        "password": mgmt_pass
    }
    
    response_auth = requests.post(url, json=payload, headers=headers, verify=False)
    if response_auth.status_code == 200:
        print("auth ok")
        payload = {}
        url =  f"https://{mgmt_ip}/api/v2/GetDeviceGroupsTree"
        r = requests.post(url, headers=headers, json=payload, verify=False, cookies=response_auth.cookies)
        cookies = response_auth.cookies
        # ПОЛУЧАЕМ ID глобальной группы
        global_gr_id = get_id_groupe(r.json()['groups'][0])

    else:
        print("auth fail")
        exit()


def get_id_groupe(groups):
    # Проверка текущей группы
    if groups.get("name") == groupe_name:
        return groups.get("id")
    # Проверка вложенных групп, если они существуют
    if "subgroups" in groups:
        for subgroup in groups["subgroups"]:  # Проходим по списку подгрупп
            result = get_id_groupe(subgroup)
            if result:  # Если id найдено, возвращаем его
                return result
    return None  # Возвращаем None, если ничего не найдено

def get_app():
    # ---------------------  GET APP ----------------------
    url = f"https://{mgmt_ip}:443/api/v2/ListApplications"
    payload = {
        "deviceGroupId": global_gr_id,
        "offset": 0,
        "limit": 10000
    }

    response = requests.request("POST", url, json=payload, headers=headers, cookies=cookies, verify=False)

    if response.status_code == 200:
        data = response.json()
        #print(data)
        app = []
        for item in data["applications"]:  
            #if item["name"] not in app_list: # если not то это спиcок исключений. 
            app_id = item["id"]           
            app.append(app_id)             
        
        return app 
    
    else:
        print(f"Error: {response.status_code} - {response.text}")
        exit()

def get_ip():
    # ---------------------  GET IP ----------------------
    url = f"https://{mgmt_ip}:443/api/v2/ListNetworkObjects"
    payload = {
        "deviceGroupId": global_gr_id,
        "objectKinds": ["OBJECT_NETWORK_KIND_IPV4_ADDRESS"],
        "offset": 0,
        "limit": 10000
    }

    response = requests.request("POST", url, json=payload, headers=headers, cookies=cookies, verify=False)

    if response.status_code == 200:
        data = response.json()
        #print(data)
        dest_objects = [obj["id"] for obj in data["addresses"] if obj["name"].startswith("Dest")]
        src_objects = [obj["id"] for obj in data["addresses"] if obj["name"].startswith("Source")]
        return dest_objects, src_objects
    else:
        print(f"Error: {response.status_code} - {response.text}")
        exit()


def get_service():
    # ---------------------  GET SERVICE ----------------------
    url = f"https://{mgmt_ip}:443/api/v2/ListServices"

    payload = {
        "deviceGroupId": global_gr_id,
    
        "objectOriginKinds": ["OBJECT_ORIGIN_KIND_CUSTOM"],
        "offset": 0,
        "limit": 10000
    }

    response = requests.request("POST", url, json=payload,  headers=headers, cookies=cookies, verify=False)

    if response.status_code == 200:
        data = response.json()
        id_dict_services = [obj["id"] for obj in data["services"]]
        return id_dict_services
    else:
        print(f"Error: {response.status_code} - {response.text}")
        exit()


def get_zones():
# ---------------------  GET ZONES ----------------------

    url = f"https://{mgmt_ip}:443/api/v2/ListZones"

    payload = {
        "offset": 0,
        "limit": 10000
    }

    response = requests.request("POST", url, json=payload,  headers=headers, cookies=cookies, verify=False)

    if response.status_code == 200:
        data = response.json()
        zones = [item["id"] for item in data["zones"] if not item["name"].startswith("Local")]
        return zones
        #print(zones)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        exit()

    



def random_rules():
  auth()
  possible_action = ["SECURITY_RULE_ACTION_DROP", "SECURITY_RULE_ACTION_ALLOW", "SECURITY_RULE_ACTION_DENY","SECURITY_RULE_ACTION_RESET_SERVER","SECURITY_RULE_ACTION_RESET_CLIENT","SECURITY_RULE_ACTION_RESET_BOTH"]
  possible_log = ["SECURITY_RULE_LOG_MODE_NO_LOG", "SECURITY_RULE_LOG_MODE_AT_SESSION_START", "SECURITY_RULE_LOG_MODE_AT_SESSION_END", "SECURITY_RULE_LOG_MODE_AT_RULE_HIT", "SECURITY_RULE_LOG_MODE_AT_SESSION_START_AND_END"]
  
    
  #----------add rules ----------- 
  url_serv  = f"https://{mgmt_ip}/api/v2/CreateSecurityRule"

  dest_objects, src_objects = get_ip()
  id_dict_services = get_service()
  zones = get_zones()
  app = get_app()

  for i in range(obj_num):
    random_id_dict_services = random.sample(id_dict_services, k=5)
    random_dest_objects = random.sample(dest_objects, k=5)
    random_src_objects = random.sample(src_objects, k=5)
    random_action = random.choice(possible_action)
    random_log = random.choice(possible_log)
    random_zone_src = random.choice(zones)
    random_zone_dst = random.choice(zones)
    random_app = random.choice(app)
    payload = {
    "deviceGroupId": global_gr_id,
    "precedence": "pre",
    "position": i + 1,
    "enabled": True,
    "name": f"Random_Rule_{i}",
    "description": "",
    "sourceZone": {
        "kind": "RULE_KIND_LIST",
        "objects": {
            "array": [
                random_zone_src
            ]
        }
    },
    "destinationZone": {
        "kind": "RULE_KIND_LIST",
        "objects": {
            "array": [
                random_zone_dst
            ]
        }
    },
    "sourceAddr": {
        "kind": "RULE_KIND_LIST",
        "objects": {
            "array": 
                random_src_objects
            
        }
    },
    "destinationAddr": {
        "kind": "RULE_KIND_LIST",
        "objects": {
            "array": 
                random_dest_objects
            
        }
    },
    "sourceUser": {
        "kind": "RULE_USER_KIND_ANY",
        "objects": {}
    },
    "service": {
        "kind": "RULE_KIND_LIST",
        "objects": {
            "array": 
                random_id_dict_services
        }
    },
    "application": {
        "kind": "RULE_KIND_LIST",
        "objects": {
        "array": [
                random_app
            ]
        }
    },
    "urlCategory": {
        "kind": "RULE_KIND_ANY",
        "objects": {}
    },
    "action": random_action,
    "logMode": random_log
    }
    
    
    headers = {"Content-Type": "application/json"}
    response_ser = requests.post(url_serv, json=payload, headers=headers, verify=False, cookies=cookies)
    print(f"Random_Rule_{i}: {response_ser.json()}")




mgmt_ip = "192.168.1.100"
mgmt_login =  "admin"
mgmt_pass = "xxXX1234$"
obj_num = 10
groupe_name= "Global"


random_rules()