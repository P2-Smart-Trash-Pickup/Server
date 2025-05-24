import json
def get_data_path() -> str:
    return "C:/Users/MartinNammat/Documents/Programming-2/Uni/P2/El-bil/data/" 

def load_elevation_matrix() -> list[list[list[list[float]]]]:
    data_path = get_data_path()
    elevation_matrix = []
    with open(data_path + "molok_elcom_matrix.json","r") as f:
        elevation_matrix = json.load(f)
    return elevation_matrix

def load_full_elevation_matrix() -> list[list[list[list[float]]]]:
    data_path = get_data_path()
    elevation_matrix = []
    with open(data_path + "molok_elevation_matrix2.json","r") as f:
        elevation_matrix = json.load(f)
    return elevation_matrix

def load_time_matrix() -> list[list[float]]:
    data_path = get_data_path()
    time_matrix= []
    with open(data_path + "molok_time_matrix2.json","r") as f:
        time_matrix = json.load(f)
    return time_matrix 

def load_fill_rate() -> list[float]:
    data_path = get_data_path()
    fill_rates = []
    with open(data_path + "fill_rates.json","r") as f:
        fill_rates = json.load(f)
    return fill_rates
def load_distance_matrix() -> list[list[float]]:
    data_path = get_data_path()
    distance_matrix = []
    with open(data_path + "molok_distance_matrix2.json","r") as f:
        distance_matrix= json.load(f)
    return distance_matrix 
def load_moloks():
    data_path = get_data_path()
    molokker= []
    with open(data_path + "molokker.json","r") as f:
        molokker= json.load(f)
    return molokker 
def load_max_fille():
    data_path = get_data_path()
    molokker= []
    max_fill = [0]
    with open(data_path + "molokker.json","r") as f:
        molokker= json.load(f)
    for m in molokker[1:]:
        max_fill.append(m["max_fill"])
    return max_fill 
def load_date_molok():
    data_path = get_data_path()
    molokker= []
    with open(data_path + "empty_data.json","r") as f:
        molokker= json.load(f)
    return molokker 





