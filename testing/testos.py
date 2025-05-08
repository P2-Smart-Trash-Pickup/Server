import pandas as pd
import requests
import json

EXCEL_PATH = "Rute 835 - Papir.xlsx"
SHEET_NAME = "ebbr_07-05-2025 (1)"
ADDRESS_COLUMN = "Adresse"
SIZE_COLUMN = "Størrelse"

df = pd.read_excel(EXCEL_PATH, sheet_name=SHEET_NAME)

def convert_strings_to_liters(s: str) -> int:
    if s == "Papir delvist-nedgravet Komm.":
        return 3000
    s_l = s.split(" ")
    num_str = s_l[1]
    if num_str[-1] == "L":
        num = int(num_str[:-1])
        return num
    elif s_l[2] == "L":
        num = int(num_str)
        return num
    C = int(float(num_str.replace(",","."))*1000)
    return C
print(len(set(df["Fuld adresse"].tolist())))
adress_and_fill = zip(df["Fuld adresse"].tolist(),df["Materieltype"].tolist())
unique = []
for val in adress_and_fill:
    is_seen = False
    for u in unique:
        if u[0] == val[0]:
            is_seen = True
            break
    if not is_seen:
        unique.append(val)

fill_count = [convert_strings_to_liters(s[1]) for s in unique]

out_obj = []
iteration = 0
max_length = len(unique)
not_found = [] 
for data in zip(unique,fill_count):
    print(f"{iteration} of {max_length}")
    adress = data[0][0].split(" ")
    street = adress[0]  
    i = 1
    while street[-1] != ",":
        street += " " +adress[i]
        i += 1
    street = street[:-1]
    postalcode = adress[i]

    url = f"http://localhost:8080/search.php?street={street}&postalcode={postalcode}"
    resp = requests.request(url=url,method="GET")
    resp_json = resp.json()
    if len(resp_json) == 0:
        print(adress)
        print(street)
        print(resp_json)
        not_found.append(data[0][0])
        continue
        #raise Exception("No thang")
    lon = float(resp_json[0]["lon"])
    lat = float(resp_json[0]["lat"])
    obj = {"adress":data[0][0],"lon":lon,"lat":lat,"max_fill":data[1]}
    out_obj.append(obj)
    iteration += 1
for val in not_found:
    print(val)
out_obj.append({"adress": "Klosterholmsgade 29, 9240 Nibe", "lon": 9.631236, "lat": 56.981334, "max_fill": 3000})
print(len(out_obj))
out_json = json.dumps(out_obj)
with open("molokker.json","w") as f:
    f.write(out_json)
