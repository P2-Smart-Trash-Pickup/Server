import json
poly_matrix = []
import pandas
with open('../data/molok_polyline_matrix.json', 'r') as f:
    poly_matrix= json.loads(f.read()) 
elevaiton_matrix = []
with open('../data/molok_elevation_matrix.json', 'r') as f:
    elevaiton_matrix = json.loads(f.read()) 
molok = []
with open('../data/molokker_class.json', 'r') as f:
    molok= json.loads(f.read()) 

mol = pandas.read_excel("../testing/Rute 835 - Papir - Tømningstidspunkter.xlsx",sheet_name="ebbr_07-05-2025 (3)")
adresses = mol["Fuld adresse"].tolist()
for adress in adresses:
    if not molok.get(adress):
        raise Exception("Fack")

print(len(molok.keys()))
print(len(elevaiton_matrix))
"""
for line_idx in range(len(poly_matrix)):
    line = poly_matrix[line_idx]
    if line.index("") != line_idx:
        print(line_idx)
"""
