import sys
from typing import Any
from PySide6 import  QtGui, QtWidgets
import random
import math
from itertools import product

from PySide6.QtCore import  QPointF, QRect, Qt

from painter_drawers import drawCircleRect, drawLineArrow 

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
def print_solution(data, manager, routing, solution):
    """Prints solution on console."""
    print(f"Objective: {solution.ObjectiveValue()}")
    total_distance = 0
    for vehicle_id in range(data["num_vehicles"]):
        if not routing.IsVehicleUsed(solution, vehicle_id):
            continue
        index = routing.Start(vehicle_id)
        plan_output = f"Route for vehicle {vehicle_id}:\n"
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += f" {manager.IndexToNode(index)} -> "
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id
            )
        plan_output += f"{manager.IndexToNode(index)}\n"
        plan_output += f"Distance of the route: {route_distance}m\n"
        print(plan_output)
        total_distance += route_distance
    print(f"Total Distance of all routes: {total_distance}m")

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()


        self.custom_layout = QtWidgets.QVBoxLayout()

        self.form_label = QtWidgets.QLabel()
        self.form_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.random_marker_amount = QtWidgets.QLineEdit()
        self.random_marker_amount.setValidator(QtGui.QIntValidator())
        self.random_marker_amount.returnPressed.connect(self.simulate)

        self.random_truck_amount = QtWidgets.QLineEdit()
        self.random_truck_amount.setValidator(QtGui.QIntValidator())
        self.random_truck_amount.returnPressed.connect(self.simulate)

        self.vehicle_capacity_input = QtWidgets.QLineEdit()
        self.vehicle_capacity_input.setValidator(QtGui.QIntValidator())
        self.vehicle_capacity_input.returnPressed.connect(self.simulate)

        self.button = QtWidgets.QPushButton("Press")
        self.button.clicked.connect(self.simulate)


        widget = QtWidgets.QWidget()

        self.label = QtWidgets.QLabel()

        self.box_amoun_x = 16
        self.box_amoun_y = 12 

        self.box_size = 50

        self.canvas_width = self.box_size*self.box_amoun_x 
        self.canvas_height = self.box_size*self.box_amoun_y 

        self.canvas = QtGui.QPixmap(self.canvas_width, self.canvas_height)
        self.painter = QtGui.QPainter(self.canvas)

        self.bg_col = "#FFC8C8"

        self.label.setPixmap(self.canvas)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.form_layout = QtWidgets.QFormLayout()
        self.form_layout.addRow("Marker amount:", self.random_marker_amount)
        self.form_layout.addRow("Truck amount:", self.random_truck_amount)
        self.form_layout.addRow("Vehicle capacity:", self.vehicle_capacity_input)

        self.custom_layout.addWidget(self.form_label)
        self.custom_layout.addLayout(self.form_layout)
        self.custom_layout.addWidget(self.button)
        self.custom_layout.addWidget(self.label)

        self.custom_layout.addStretch()

        widget.setLayout(self.custom_layout)

        self.setCentralWidget(widget)
        print("Nice 0")
        self.painter = self.draw_background(self.painter)

        self.painter = QtGui.QPainter(self.canvas)


    def draw_background(self,painter:QtGui.QPainter) -> QtGui.QPainter:
        painter.setPen(QtGui.QColor.fromString("#000000"))
        painter.setBrush(QtGui.QColor.fromString(self.bg_col))
        painter.drawRect(0,0,self.canvas_width,self.canvas_height)

        for x in range(self.box_amoun_x):

            float_x = float(x)
            start_point = QPointF(float_x*self.box_size,0)
            end_point = QPointF(float_x*self.box_size,self.canvas_height)
            painter.drawLine(start_point,end_point)

        for y in range(self.box_amoun_y):
            float_y = float(y)
            start_point = QPointF(0, float_y*self.box_size)
            end_point = QPointF(self.canvas_width, float_y*self.box_size)
            painter.drawLine(start_point,end_point)

        painter.end()
        self.label.setPixmap(self.canvas)

        return painter
    def get_user_input(self) -> dict[str,int]:
        marker_amount_str = self.random_marker_amount.text()
        truck_amount_str = self.random_truck_amount.text()
        capacity_vehicle_str = self.vehicle_capacity_input.text()

        if not marker_amount_str:
            self.form_label.setText("No input for marker amount")
            return {}

        if not truck_amount_str:
            self.form_label.setText("No input for truck amount")
            return {}

        if not capacity_vehicle_str:
            self.form_label.setText("No input for truck capacity")
            return {}

        self.form_label.setText("")

        marker_amount= int(marker_amount_str)
        truck_amount_int = int(truck_amount_str)
        capacity_vehicle_int= int(capacity_vehicle_str)

        out_obj = {}
        out_obj["marker_amount"] = marker_amount
        out_obj["truck_amount"] = truck_amount_int
        out_obj["vehicle_capacity"] = capacity_vehicle_int

        return out_obj

    def generate_cords(self,cord_amount,max_x:int,max_y:int) -> list[tuple[int,int]]:
        coord = list(product(range(max_x),range(max_y)))
        random_cords = random.sample(coord,cord_amount+1)

        return random_cords

    def draw_points(self,painter:QtGui.QPainter,random_cords:list[tuple[int,int]]) -> QtGui.QPainter:
        start_cord = random_cords[0]
        
        pen = QtGui.QPen()
        pen.setWidth(5)

        painter = drawCircleRect(painter=self.painter,x_cord=start_cord[0]*self.box_size,y_cord=start_cord[1]*self.box_size,radius=self.box_size,line_color="#49d164",fill_color="#49d164")

        for i in range(1,len(random_cords)):
            color = "%06x" % random.randint(0,0xFFFFFF)

            pen.setColor("#"+color)

            y_cord = random_cords[i][1]*self.box_size
            x_cord = random_cords[i][0]*self.box_size

            rectangle = QRect(x_cord,y_cord,self.box_size,self.box_size)

            painter = drawCircleRect(painter=self.painter,x_cord=x_cord,y_cord=y_cord,radius=self.box_size,line_color="#"+color,fill_color=self.bg_col)

            pen.setColor("#000000")
            painter.setPen(pen)
            painter.drawText(rectangle,Qt.AlignmentFlag.AlignCenter,str(i))

        return painter


    def def_setup_data(self,cords:list[tuple[int,int]],user_input:dict[str,int]):

        temp_distances = []
        distances = []
        for current_cord in cords:
            for cord in cords:
                distance = math.sqrt((cord[1]-current_cord[1])**2+(cord[0]-current_cord[0])**2)
                temp_distances.append(int(distance))
            distances.append(temp_distances)

        data = {}
        data["distance_matrix"] = distances 
        data["demands"] = [0] 
        for _ in range(1,len(distances)):
            data["demands"].append(1)

        print(data["demands"])
        data["num_vehicles"] = user_input["truck_amount"] 

        print(data["num_vehicles"])

        data["vehicle_capacities"] = [user_input["vehicle_capacity"] for _ in range (user_input["truck_amount"])] 

        print(data["vehicle_capacities"])
        data["depot"] = 0


        return data 

    def solve_vrp(self,data) -> tuple[pywrapcp.RoutingIndexManager,pywrapcp.RoutingModel,type[Any]] | None:

        manager = pywrapcp.RoutingIndexManager(
            len(data["distance_matrix"]), data["num_vehicles"], data["depot"]
        )
        

        routing = pywrapcp.RoutingModel(manager)


        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data["distance_matrix"][from_node][to_node]

        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        routing.SetFixedCostOfAllVehicles(1000000)
        # Add Capacity constraint.
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return data["demands"][from_node]

        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data["vehicle_capacities"],  # vehicle maximum capacities
            True,  # start cumul to zero
            "Capacity",
        )

        # Add Distance constraint.
        dimension_name = "Distance"
        routing.AddDimension(
            transit_callback_index,
            0,  # no slack
            3000,  # vehicle maximum travel distance
            True,  # start cumul to zero
            dimension_name,
        )
        distance_dimension = routing.GetDimensionOrDie(dimension_name)
        distance_dimension.SetGlobalSpanCostCoefficient(100)


        # Setting first solution heuristic.
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.FromSeconds(10)

        # Solve the problem.
        solution = routing.SolveWithParameters(search_parameters)
        if not solution:
            print("NOOOOO")
            self.painter.end()
            self.label.setPixmap(self.canvas)
            return 
        print_solution(data, manager, routing, solution)

        return manager,routing,solution

    def draw_solution(self,painter:QtGui.QPainter,user_input:dict[str,int],solution,routing:pywrapcp.RoutingModel,manager:pywrapcp.RoutingIndexManager,cords:list[tuple[int,int]]) -> QtGui.QPainter:
        for vehicle_index in range(user_input["truck_amount"]):
            if not routing.IsVehicleUsed(solution, vehicle_index):
                continue

            index = routing.Start(vehicle_index)

            old_point_cords = cords[manager.IndexToNode(index)] 
            old_point = QPointF(old_point_cords[0]*self.box_size + self.box_size/2,old_point_cords[1]*self.box_size + self.box_size/2)
            new_point = old_point

            index = solution.Value(routing.NextVar(index))

            vehicle_color = "%06x" % random.randint(0,0xFFFFFF)

            while not routing.IsEnd(index):
                new_point_cord = cords[manager.IndexToNode(index)] 
                new_point = QPointF(new_point_cord[0]*self.box_size + self.box_size/2,new_point_cord[1]*self.box_size + self.box_size/2)

                painter = drawLineArrow(painter=painter,old_point=old_point,new_point=new_point,line_color="#"+vehicle_color,arrow_color="#"+vehicle_color)

                old_point=new_point 

                index = solution.Value(routing.NextVar(index))

            new_point_cord = cords[manager.IndexToNode(index)] 
            new_point = QPointF(new_point_cord[0]*self.box_size + self.box_size/2,new_point_cord[1]*self.box_size + self.box_size/2)

            painter = drawLineArrow(painter=painter,old_point=old_point,new_point=new_point,line_color="#"+vehicle_color,arrow_color="#"+vehicle_color)

        painter.end()
        self.label.setPixmap(self.canvas)

        return painter
    def simulate(self):
        user_input = self.get_user_input()
        self.painter = self.draw_background(self.painter)

        self.painter = QtGui.QPainter(self.canvas)
        print("Nice 1")
        cords = self.generate_cords(user_input["marker_amount"],self.box_amoun_x,self.box_amoun_y)
        self.painter = self.draw_points(self.painter,cords)
        print("Nice 2")
        data = self.def_setup_data(cords,user_input)
        output = self.solve_vrp(data)
        if output == None:
            return
        manger,routing,solution = output
        self.painter = self.draw_solution(self.painter,user_input,solution,routing,manger,cords)
        print("Nice 3")
        self.painter = QtGui.QPainter(self.canvas)

random.seed()
app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
