import pandas as pd


df = pd.read_excel("C:/Users/MartinNammat/Documents/Programming-2/Uni/P2/El-bil/testing/Rute 835 - Papir - Tømningstidspunkter.xlsx",sheet_name="ebbr_07-05-2025 (3)")

days = set(df["Tømningsdag"].tolist())

print(days)
