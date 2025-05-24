import matplotlib.pyplot as plt

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import json
import cartopy.io.img_tiles as cimgt

import random
from shapely.geometry import LineString

cust_plan = []
with open("../data/optimized_nord_energy.json", "r") as f:
    cust_plan = json.load(f)

mols = []
with open("../data/molokker.json", "r") as f:
    mols = json.load(f)
polies = []
with open("../data/molok_polyline_matrix2.json", "r") as f:
    polies = json.load(f)

cords = []

min_lon = float("inf")
max_lon = -float("inf")

min_lat = float("inf")

max_lat = -float("inf")

for day in cust_plan:
    cords.append([])
    for route in day:
        for point in route:
            mol = mols[point]
            lon = mol["lon"]
            lat = mol["lat"]
            min_lon = lon if lon < min_lon else min_lon
            max_lon = lon if lon > max_lon else max_lon

            min_lat = lat if lat < min_lat else min_lat
            max_lat = lat if lat > max_lat else max_lat

            addres = mol["adress"]
            out_obj = {"name": addres, "lon": lon, "lat": lat, "point": point}
            cords[-1].append(out_obj)
center_lat = (max_lat + min_lat) / 2
center_lon = (max_lon + min_lon) / 2
zoom = 0.000075
zoom = 0.2


def main():
    ax = plt.axes(projection=ccrs.PlateCarree())
    # ax.set_extent([min_lon,max_lon,min_lat,max_lat], crs=ccrs.PlateCarree())
    osm_img = cimgt.OSM()
    ax.add_image(osm_img, 10)

    # ax.add_feature(cfeature.LAND)
    # ax.add_feature(cfeature.OCEAN)
    # ax.add_feature(cfeature.COASTLINE)
    # ax.add_feature(cfeature.BORDERS, linestyle=':')
    # ax.add_feature(cfeature.LAKES, alpha=0.5)
    # ax.add_feature(cfeature.RIVERS)
    ax.set_extent(
        [
            center_lon - (zoom * 2.0),
            center_lon + (zoom * 2.0),
            center_lat - zoom,
            center_lat + zoom,
        ]
    )

    # Generating a random number in between 0 and 2^24

    # Converting that number from base-10
    # (decimal) to base-16 (hexadecimal)
    for route in cords:
        r = str(hex(random.randint(0, 255))[2:])
        g = str(hex(random.randint(0, 255))[2:])
        b = str(hex(random.randint(0, 255))[2:])
        r = "0" + r if len(r) == 1 else r
        g = "0" + g if len(g) == 1 else g
        b = "0" + b if len(b) == 1 else b

        lons = []
        lats = []
        for idx in range(len(route) - 1):
            cord = route[idx]
            next_cord = route[idx + 1]
            poly = polies[cord["point"]][next_cord["point"]]

            pol_lon = [i[1] for i in poly]
            pol_lat = [i[0] for i in poly]
            line = LineString(zip(pol_lon, pol_lat))
            ax.add_geometries(
                [line],
                crs=ccrs.PlateCarree(),
                edgecolors=f"#{r}{g}{b}",
                facecolor="none",
            )
            lons.append(cord["lon"])
            lats.append(cord["lat"])
            # kax.plot(cord["lon"],cord["lat"],"o",color=f"#{r}{g}{b}",transform=ccrs.PlateCarree())
        ax.scatter(
            lons,
            lats,
            s=30,
            c=f"#{r}{g}{b}",
            edgecolors="black",
            linewidths=1,
            transform=ccrs.PlateCarree(),
        )

    ax.plot(
        cords[0][0]["lon"],
        cords[0][0]["lat"],
        "o",
        color=f"#FFFFFF",
        transform=ccrs.PlateCarree(),
    )

    plt.show()


if __name__ == "__main__":
    main()
