import json

import pandas as pd

EXCEL_PATH = "Rute 835 - Papir - Tømningstidspunkter.xlsx"
SHEET_NAME = "ebbr_07-05-2025 (3)"
ADDRESS_COLUMN = "Adresse"
SIZE_COLUMN = "Størrelse"

df = pd.read_excel(EXCEL_PATH,sheet_name=SHEET_NAME)

out_obj = {}

for i in zip(df["Fuld adresse"].tolist(),df["Tømningsdato"].tolist(),df["Tømningsklokkeslæt"].tolist()):
    print(i[1])
    date = str(i[1]).split("-")
    print(date)
    day = int(date[2].split(" ")[0])
    month = int(date[1])
    year = int(date[0])

    has_year = out_obj.get(year)

    day_obj = {"adress":i[0],"time":i[2]}

    if has_year:
        has_month = out_obj[year].get(month)
        if has_month:
            has_day = out_obj[year][month].get(day)
            if has_day:
                out_obj[year][month][day].append(day_obj)
                continue
            out_obj[year][month][day] = [day_obj]
            continue
        out_obj[year][month] = {day:[day_obj]}
        continue
    out_obj[year] = {month:{day:[day_obj]}}
for months in out_obj.values():
    for days in months.values():
        for val in days.values():
            val.sort(key=lambda x:x["time"])
out_json = json.dumps(out_obj)

with open("empty_data.json","w") as f:
    f.write(out_json)


