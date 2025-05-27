import requests
import time


url = "http://localhost:8989/route?profile=truck&elevation=true&instructions=false&points_encoded=false"

points = [[ 9.921586,57.025898], [ 9.921586,57.025898]] 
for i in points:
    url +="&"
    url +=f"point={i[1]},{i[0]}"
s = requests.session()
start = time.time()

resp = s.get(url=url).json()
print(resp)
