import json
import folium
import requests

import sys
import random

from PySide6 import QtCore, QtWidgets, QtGui, QtWebEngineWidgets

api_key = "5b3ce3597851110001cf6248ed50866be076409fb8f609ad87bd414c"


molokker_file_name = "molokker.geojson"

molokker_data = "" 

with open(molokker_file_name) as f:
    molokker_data = json.load(f)

molokker_features = molokker_data["features"]

avg_lon = 0
avg_lat = 0

min_lat = 57.03272058746086 
min_lon = 9.912306845024473 

max_lat = 57.04921621947224
max_lon = 9.946947394844035 

header = {"Authorization":api_key,'Content-Type': 'application/json'}

optimization_url = "https://api.openrouteservice.org/optimization"
directions_url = "https://api.openrouteservice.org/v2/directions/driving-car/geojson"
matrix_url = "https://api.openrouteservice.org/v2/matrix/driving-car"

m = folium.Map()
m.fit_bounds([[max_lat,max_lon],[min_lat,min_lon]],padding=(11,11))

html_file = m._repr_html_()

app = QtWidgets.QApplication(sys.argv)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Testing")

        self.custom_layout = QtWidgets.QVBoxLayout()

        self.form_label = QtWidgets.QLabel()
        self.form_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.random_marker_amount = QtWidgets.QLineEdit()
        self.random_marker_amount.setValidator(QtGui.QIntValidator())
        self.random_marker_amount.returnPressed.connect(self.changeHTML)

        self.random_truck_amount = QtWidgets.QLineEdit()
        self.random_truck_amount.setValidator(QtGui.QIntValidator())
        self.random_truck_amount.returnPressed.connect(self.changeHTML)

        self.truck_capacity = QtWidgets.QLineEdit()
        self.truck_capacity.setValidator(QtGui.QIntValidator())
        self.truck_capacity.returnPressed.connect(self.changeHTML)

        self.button = QtWidgets.QPushButton("Press")
        self.button.clicked.connect(self.changeHTML)

        self.webV = QtWebEngineWidgets.QWebEngineView()
        self.webV.setHtml(html_file)

        self.webV.show()

        widget = QtWidgets.QWidget()

        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.addRow("Marker amount:", self.random_marker_amount)
        self.form_layout.addRow("Truck amount:", self.random_truck_amount)
        self.form_layout.addRow("Truck capacity:", self.truck_capacity)

        self.custom_layout.addWidget(self.form_label)
        self.custom_layout.addLayout(self.form_layout)
        self.custom_layout.addWidget(self.button)
        self.custom_layout.addWidget(self.webV)

        self.custom_layout.addStretch()

        widget.setLayout(self.custom_layout)

        self.setCentralWidget(widget)

    def changeHTML(self):

        out_obj = {"shipments":[],"vehicles":[]}

        marker_amount_str = self.random_marker_amount.text()
        truck_amount_str = self.random_truck_amount.text()
        truck_capacity_str = self.truck_capacity.text()
        if not marker_amount_str:
            self.form_label.setText("No input for marker amount")
            return

        if not truck_amount_str:
            self.form_label.setText("No input for truck amount")
            return

        if not truck_capacity_str:
            self.form_label.setText("No input for truck capacity")
            return

        self.form_label.setText("")

        marker_amount_int = int(marker_amount_str)
        truck_amount_int = int(truck_amount_str)
        truck_capacity_int= int(truck_capacity_str)

        m = folium.Map()
        m.fit_bounds([[max_lat,max_lon],[min_lat,min_lon]],padding=(11,11))

        random.seed = 5

        rand_lat = random.uniform(min_lat, max_lat)
        rand_long = random.uniform(min_lon, max_lon)

        delivery_location = [round(rand_long,5),round(rand_lat,5)]

        folium.Marker(
            location=[delivery_location[1],delivery_location[0]],
            icon=folium.Icon(color="blue")
        ).add_to(m)

        rand_lat = random.uniform(min_lat, max_lat)
        rand_long = random.uniform(min_lon, max_lon)

        vehicle_location = [round(rand_long,5),round(rand_lat,5)]

        folium.Marker(
            location=[delivery_location[1],delivery_location[0]],
            icon=folium.Icon(color="blue")
        ).add_to(m)

        locations = []

        for i in range(marker_amount_int):

            rand_lat = random.uniform(min_lat, max_lat)
            rand_long = random.uniform(min_lon, max_lon)

            folium.Marker(
                location=[rand_lat,rand_long],
                icon=folium.Icon(color="red")
            ).add_to(m)


        
        hex_converter = '#%02x%02x%02x' 

        vehicle_colors = [] 

        out_str = json.dumps(out_obj)


        response = requests.post(url=optimization_url,data=out_str,headers=header)

        resp_obj = response.json()
        print(resp_obj)


        optimized_routes = resp_obj["routes"] 


        for id in range(len(optimized_routes)):

            vehicle_1 = optimized_routes[id]
            vehicle_1_steps= vehicle_1["steps"]
            locations = []

            for step in vehicle_1_steps:
                locations.append(step["location"])

            directions_obj = {"coordinates":locations}

            directions_obj_str = json.dumps(directions_obj)

            response = requests.post(url=directions_url,data=directions_obj_str,headers=header)

            resp_obj = response.json()

            route = resp_obj["features"][0]["geometry"]["coordinates"]

            for i in range(len(route)):
                temp = route[i][0]
                route[i][0] = route[i][1]
                route[i][1] = temp
            folium.PolyLine(
                locations=route,
                color=vehicle_colors[id],
                weight=10
            ).add_to(m)
        
        self.webV.setHtml(m._repr_html_())
        self.webV.show()


window = MainWindow() 

window.show()

app.exec()



