const resp = await fetch(" http://localhost:8080/optimized_cust_energy");

const temp = await resp.json();
const plan = temp["msg"];

const resp2 = await fetch("http://localhost:8080/moloks");
const temp2 = await resp2.json();
const molokker = temp2["msg"];

const depot = molokker[0];
const depot_lat = depot["lat"];
const depot_lon = depot["lon"];

let max_lat = -100;
let min_lat = 100;

let max_lon = -100;
let min_lon = 100;

const map = L.map("map").setView([0, 0], 11);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution:
    '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

const cols = [];

for (let day_idx = 0; day_idx < plan.length; day_idx++) {
  const routes = plan[day_idx];

  const day_col =
    "#" + ((Math.random() * 0xffffff) << 0).toString(16).padStart(6, "0");
  cols.push(day_col);

  for (let route_idx = 0; route_idx < routes.length; route_idx++) {
    const route = routes[route_idx];

    for (let cust_idx = 0; cust_idx < route.length - 1; cust_idx++) {
      const point = route[cust_idx];
      const next_point = route[cust_idx + 1];
      const mol = molokker[point];
      const lat = mol["lat"];
      const lon = mol["lon"];

      max_lat = lat > max_lat ? lat : max_lat;
      min_lat = lat < min_lat ? lat : min_lat;

      max_lon = lon > max_lon ? lon : max_lon;
      min_lon = lon < min_lon ? lon : min_lon;

      L.circleMarker([lat, lon], {
        color: "black",
        fillColor: day_col,
        fillOpacity: 1,
        radius: 2,
        weight: 1,
      }).addTo(map);
    }
  }
}

map.fitBounds([
  [min_lat, min_lon],
  [max_lat, max_lon],
]);

for (let day_idx = 0; day_idx < plan.length; day_idx++) {
  const routes = plan[day_idx];

  const day_col = cols[day_idx];

  for (let route_idx = 0; route_idx < routes.length; route_idx++) {
    const route = routes[route_idx];

    if (route.length <= 2) {
      continue;
    }
    const json_route = JSON.stringify(route);
    const resp3 = await fetch(`http://localhost:8080/${json_route}`);
    const polies = await resp3.json();
    for (const poly of polies["msg"]) {
      L.polyline(poly, { color: day_col }).addTo(map);
    }
  }
}
