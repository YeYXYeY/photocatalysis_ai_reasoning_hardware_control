import requests
import yaml


class Trans200:
    pass

# with open('config.yaml', 'r', encoding='utf-8') as f:
#     param = yaml.safe_load(f)

# fleet_host = param["agv_web"]['fleet_host']
# fleet_port = param["agv_web"]['fleet_port']

# # ID
# work_id = "your_work_id"

# url = f"http://{fleet_host}:{fleet_port}/api/v3/missionWorks/{work_id}/controls/pause"

# # response = requests.post(url)

# # if response.status_code == 200:
# # print(" ")
# # else:
# #     print("Error:", response.status_code)

# try:
#     response = requests.get(url, timeout=10)

# response.raise_for_status() # HTTP

# print(" ")
#     print(response.json())

# except requests.Timeout:
# print(" ")
# except requests.HTTPError as e:
# print(f"HTTP :{e}")
# except requests.RequestException:
# print(" ")
