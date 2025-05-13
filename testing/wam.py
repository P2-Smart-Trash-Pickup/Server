import folium
bb = [[9.921628, 57.025805], [9.921628, 57.025805]]
map = folium.Map()
poly =[[9.921628, 57.025805, 5.0], [9.921628, 57.025805, 5.0]] 

folium.PolyLine(locations=[[val[1],val[0],val[2]] for val in poly]).add_to(map)

map.fit_bounds([[bb[0][1],bb[0][0]],[bb[1][1],bb[1][0]]])

map.save("gra.html")
