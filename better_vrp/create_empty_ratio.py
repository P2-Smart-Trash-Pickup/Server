from file_manipulation import get_data_path, load_moloks
import pandas as pd
import json

data_path = get_data_path()
moloks = load_moloks()

fill_rate = [0] + [0 for _ in range(len(moloks) - 1)]

df = pd.read_excel(
    "../testing/Rute 835 - Papir - Tømningstidspunkter.xlsx",
    sheet_name="ebbr_07-05-2025 (3)",
)

mols = df["Fuld adresse"].tolist()
days = df["Tømningsdag"].tolist()

comb = []
for i, mol in enumerate(mols):
    have_seen = False
    for b in comb:
        if b[0] == mol:
            have_seen = True
            break
    if have_seen:
        continue
    comb.append((mol, days[i]))


for val in comb:
    adress = val[0]
    su = None
    for id, mol in enumerate(moloks):
        if mol["adress"] == adress:
            su = id
            break
    if su == None:
        raise Exception("FUCK")

    se = val[1]
    if type(se) is float:
        fill_rate[su] = 1
        continue

    fill_r = 2 if "+" in se else 1

    fill_rate[su] = fill_r
fill_rate[0] = 0

with open("nord_fill.json", "w") as f:
    json.dump(fill_rate, f)
