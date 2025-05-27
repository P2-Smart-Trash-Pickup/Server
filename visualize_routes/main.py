import io
import sys
from PySide6 import QtWidgets, QtWebEngineWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel
import folium
import json
import polyline
import random
import pandas as pd
from pathlib import Path
root_folder = str(Path(__file__).parent.parent)
def random_hex_col():
    color = random.randrange(0, 2**24)
     
    hex_color = hex(color)
    return "#"+str(hex_color)[2:]
class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.molokker = {} 
        self.molokker_date = {} 
        self.poly_line_data = [] 
        self.better_routes = {} 
        self.index = 0

        with open(root_folder+"/data/molokker_class.json","r") as f:
            self.molokker = json.loads(f.read())

        with open(root_folder+"/data/empty_data.json","r") as f:
            self.molokker_date = json.loads(f.read())

        with open(root_folder+"/data/molok_polyline_matrix2.json","r") as f:
            self.poly_line_data= json.loads(f.read())

        with open(root_folder+"/data/better.json","r") as f:
            self.better_routes= json.loads(f.read())

        self.molok_names = list(self.molokker.keys())

        self.toggled = False

        self.depot_name = "Over Bækken 2, 9000 Aalborg"

        self.depot = self.molokker[self.depot_name]


        self.widget = QtWidgets.QWidget(self)
        self.layouts = QtWidgets.QGridLayout(self.widget)
        welp = QtWidgets.QWidget()
        button_layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.Direction.TopToBottom,welp)

        date_list = QtWidgets.QListView(welp)
        self.model = QStandardItemModel()
        dates = []


        for years in self.molokker_date.keys():
            for months in self.molokker_date[years].keys():
                for days in self.molokker_date[years][months].keys():
                    dates.append(f"{days}-{months}-{years}")
        s1 = pd.Series(dates)
        s2 = pd.to_datetime(s1,dayfirst=True).sort_values()
        s3 = s2.dt.strftime("%d-%m-%Y").tolist()
        for val in s3:
            item = QStandardItem(val)
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.model.appendRow(item)
        first_item = self.model.item(0,0)

        first_item.setCheckState(Qt.CheckState.Checked)
        first_date = first_item.text().split("-")

        iter = 0
        for val in first_date:
            if len(val) > 1 and val[0] == "0":
                val = val[1:]
            first_date[iter] = val
            iter += 1

        map = folium.Map()

        min_lat = float("inf")
        min_lon = float("inf")

        max_lat = -float("inf")
        max_lon = -float("inf")

        depot_index = self.molok_names.index(self.depot_name)
        start_adress = self.molokker_date[first_date[-1]][first_date[-2]][first_date[-3]][0]["adress"] 
        better_start_index = self.better_routes[first_date[-1]][first_date[-2]][first_date[-3]][0]
        start_index = self.molok_names.index(start_adress)

        reg_poly= self.poly_line_data[depot_index][start_index]
        better_poly = self.poly_line_data[depot_index][better_start_index]

        folium.PolyLine(locations=better_poly,color="#0000ff").add_to(map)
        folium.PolyLine(locations=reg_poly,color="#ff0000").add_to(map)

        molok_date = self.molokker_date[first_date[-1]][first_date[-2]][first_date[-3]]
        better_molok = self.better_routes[first_date[-1]][first_date[-2]][first_date[-3]]

        for molok_idx in range(len(molok_date)): 
            molok = molok_date[molok_idx]
            better = better_molok[molok_idx]
            adress = molok["adress"]
            next_adress = self.depot_name
            next_better = 0
            if molok_idx < len(molok_date)-1:
                next_adress = molok_date[molok_idx+1]["adress"]
                next_better = better_molok[molok_idx+1]

            part1_index = self.molok_names.index(adress)
            part2_indx = self.molok_names.index(next_adress)

            encoded_poly = self.poly_line_data[part1_index][part2_indx]
            beter_enc = self.poly_line_data[better][next_better]

            if beter_enc and (self.index == 1 or self.index == 2):
                folium.PolyLine(locations=beter_enc,color="#0000ff").add_to(map)
            if encoded_poly and (self.index == 0 or self.index == 2):
                folium.PolyLine(locations=encoded_poly,color="#ff0000").add_to(map)

            adress = molok["adress"]
            molok_data = self.molokker[adress]
            lon = molok_data["lon"]
            lat = molok_data["lat"]
            bet = list(self.molokker.values())[better]
            better_lat = bet["lat"]
            better_lon = bet["lon"]

            if lat > max_lat:
                max_lat = lat
            elif lat < min_lat:
                min_lat = lat

            if lon > max_lon:
                max_lon = lon
            elif lon < min_lon:
                min_lon = lon

            folium.CircleMarker(location=[lat,lon],radius=1,popup=adress,color="#ffff00").add_to(map)

        folium.CircleMarker(location=[self.depot["lat"],self.depot["lon"]],radius=1,popup=self.depot_name,color="#ffff00").add_to(map)

        map.fit_bounds([[max_lat,min_lon],[min_lat,max_lon]],max_zoom=15)

        data = io.BytesIO()
        map.save(data, close_file=False)
        date_list.setModel(self.model)

        submit_button = QtWidgets.QPushButton("Submit",welp)
        submit_button.clicked.connect(self.update_map)

        toggle_button= QtWidgets.QPushButton("Toggle select",welp)
        toggle_button.clicked.connect(self.toggle_check)

        combo = QtWidgets.QComboBox(welp)
        combo.addItem("nord")
        combo.addItem("custom")
        combo.addItem("both")
        combo.currentIndexChanged.connect(self.on_change)




        self.w = QtWebEngineWidgets.QWebEngineView()
        self.w.setHtml(data.getvalue().decode())
        self.w.resize(640, 480)

        button_layout.addWidget(date_list)
        button_layout.addWidget(combo)
        button_layout.addWidget(toggle_button)
        button_layout.addWidget(submit_button)
        welp.setLayout(button_layout)
        self.layouts.addWidget(welp,0,0)
        self.layouts.addWidget(self.w,0,1)

        self.setCentralWidget(self.widget)

    def on_change(self,index):
        self.index = index
    def toggle_check(self):
        for i in range(self.model.rowCount()):
            action = self.model.item(i)
            if self.toggled == True:
                action.setCheckState(Qt.CheckState.Unchecked)
            else:
                action.setCheckState(Qt.CheckState.Checked)
        self.toggled = not self.toggled

    def update_map(self):


        map = folium.Map()

        min_lat = float("inf")
        min_lon = float("inf")

        max_lat = -float("inf")
        max_lon = -float("inf")

        depot_index = self.molok_names.index(self.depot_name)

        for i in range(self.model.rowCount()):

            action = self.model.item(i)
            first_date = action.text().split("-")
            start_adress = None
            better_start = None

            iter = 0
            for val in first_date:
                if len(val) > 1 and val[0] == "0":
                    val = val[1:]
                first_date[iter] = val
                iter += 1
            if action.checkState() != Qt.CheckState.Checked:
                continue


            molok_date = self.molokker_date[first_date[-1]][first_date[-2]][first_date[-3]]
            better_molok = self.better_routes[first_date[-1]][first_date[-2]][first_date[-3]]
            rand_col = random_hex_col()
            for molok_idx in range(len(molok_date)): 
                molok = molok_date[molok_idx]

                better = better_molok[molok_idx]
                adress = molok["adress"]
                next_adress = self.depot_name
                next_better = 0
                if molok_idx < len(molok_date)-1:
                    next_adress = molok_date[molok_idx+1]["adress"]
                    next_better = better_molok[molok_idx+1]

                if start_adress == None:
                    start_adress = adress
                if better_start == None:
                    better_start = better

                part1_index = self.molok_names.index(adress)
                part2_indx = self.molok_names.index(next_adress)
                encoded_poly = self.poly_line_data[part1_index][part2_indx]
                beter_enc = self.poly_line_data[better][next_better]

                if beter_enc and (self.index == 1 or self.index == 2):
                    folium.PolyLine(locations=beter_enc,color="#0000ff").add_to(map)
                if encoded_poly and (self.index == 0 or self.index == 2):
                    folium.PolyLine(locations=encoded_poly,color="#ff0000").add_to(map)



                molok_data = self.molokker[adress]
                lon = molok_data["lon"]
                lat = molok_data["lat"]

                if lat > max_lat:
                    max_lat = lat
                elif lat < min_lat:
                    min_lat = lat

                if lon > max_lon:
                    max_lon = lon
                elif lon < min_lon:
                    min_lon = lon

                folium.CircleMarker(location=[lat,lon],radius=1,popup=adress,color="#ffff00").add_to(map)

            start_index = self.molok_names.index(start_adress)
            encoded_poly = self.poly_line_data[depot_index][start_index]
            better_poly = self.poly_line_data[depot_index][better_start]
    
            if better_poly and (self.index == 1 or self.index == 2):
                folium.PolyLine(locations=better_poly,color="#0000ff").add_to(map)
            if encoded_poly and (self.index == 0 or self.index == 2):
                folium.PolyLine(locations=encoded_poly,color="#ff0000").add_to(map)

            folium.CircleMarker(location=[self.depot["lat"],self.depot["lon"]],radius=1,popup=self.depot_name,color="#ffff00").add_to(map)

        map.fit_bounds([[max_lat,min_lon],[min_lat,max_lon]],max_zoom=15)


        data = io.BytesIO()
        map.save(data, close_file=False)

        self.w = QtWebEngineWidgets.QWebEngineView()
        self.w.setHtml(data.getvalue().decode())
        self.w.resize(640, 480)

        self.layouts.removeWidget(self.w)
        self.layouts.addWidget(self.w,0,1)
        self.setCentralWidget(self.widget)
        


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()

    sys.exit(app.exec())
