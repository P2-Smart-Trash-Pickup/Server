import json
import requests

test = {'shipments': [{'amount': [1], 'skills': [1], 'pickup': {'id': 1, 'service': 300, 'location': [9.92755, 57.03823]}, 'delivery': {'id': 2, 'service': 300, 'location': [9.915, 57.03844]}}, {'amount': [1], 'skills': [1], 'pickup':{'id': 3, 'service': 300, 'location': [9.92252, 57.04736]}, 'delivery': {'id': 4, 'service': 300, 'location': [9.915, 57.03844]}}, {'amount': [1], 'skills': [1], 'pickup': {'id': 5, 'service': 300, 'location': [9.93968, 57.04767]}, 'delivery': {'id': 6, 'service': 300, 'location': [9.915, 57.03844]}}, {'amount': [1], 'skills': [1], 'pickup': {'id': 7, 'service': 300, 'location': [9.92112, 57.03692]}, 'delivery': {'id': 8, 'service': 300, 'location': [9.915, 57.03844]}}, {'amount': [1], 'skills': [1], 'pickup': {'id': 9, 'service': 300, 'location': [9.9462, 57.03494]}, 'delivery': {'id': 10, 'service': 300, 'location': [9.915, 57.03844]}}, {'amount': [1], 'skills': [1], 'pickup': {'id': 11, 'service': 300, 'location': [9.91311, 57.03388]}, 'delivery': {'id': 12, 'service': 300, 'location': [9.915, 57.03844]}}, {'amount': [1], 'skills': [1], 'pickup': {'id': 13, 'service': 300, 'location': [9.93091, 57.03431]}, 'delivery': {'id': 14, 'service': 300, 'location': [9.915, 57.03844]}}, {'amount': [1], 'skills': [1],'pickup': {'id': 15, 'service': 300, 'location': [9.92459, 57.0417]}, 'delivery': {'id': 16, 'service': 300, 'location': [9.915, 57.03844]}}, {'amount': [1], 'skills': [1], 'pickup': {'id': 17, 'service': 300, 'location': [9.91358, 57.04195]}, 'delivery': {'id': 18, 'service': 300, 'location': [9.915, 57.03844]}}, {'amount': [1], 'skills':[1], 'pickup': {'id': 19, 'service': 300, 'location': [9.94401, 57.03463]}, 'delivery': {'id': 20, 'service': 300, 'location': [9.915, 57.03844]}}], 'vehicles': [{'id': 1,  'start': [9.918, 57.0385], 'end': [9.918, 57.0385], 'capacity': [1], 'skills': [1]}, {'id': 2,  'start': [9.91944, 57.0336], 'end': [9.91944, 57.0336], 'capacity': [1], 'skills': [1]}, {'id': 3,  'start': [9.93514, 57.04215], 'end': [9.93514, 57.04215], 'capacity': [1], 'skills': [1]}]}

out_obj = json.dumps(test)

header = {'Content-Type': 'application/json'}
url = "http://solver.vroom-project.org"

response = requests.post(url=url,data=out_obj,headers=header)

obj = response.json()

print(obj)

