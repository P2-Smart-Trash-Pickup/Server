# :truck: EV Truck Garbage Collection optimizer:

> This project was developed during our 2nd semester at AAU.  
> It includes both the **algorithm** (detailed below) and a very basic UI featuring a login form and a map preview.  
> Many features were incomplete due to time constraints — see below for a breakdown.

## :white_check_mark: Implemented Features
- Algorithm
- Map Loading & Route Preview
- Basic User Setup & Login Forms

## :brain: Algorithm Overview
Our custom route optimization algorithm uses **GLS (Guided Local Search)** and other heuristic techniques to generate the most efficient trash collection routes.
Some of the key features of this algorithm is as follows:
- **Heuristic Route Optimization:**
  Utilizes **GLS** and other heuristics to find near-optimal paths under real-world constraints.

- **3D Terrain Awareness:**  
  Unlike basic 2D map solutions, our algorithm factors in **elevation changes** — a critical feature when optimizing for **electric vehicles (EVs)**, as hills dramatically affect power consumption depending on vehicle load.

- **Energy-Based Routing:**  
  Integrates **EV battery consumption modeling** to ensure any proposed route can be completed **without the need for mid-route recharging**. It dynamically calculates power requirements based on terrain and trash load.

> **Result:**  
> Compared to our stakeholders' baseline routes, our solution achieved an estimated **30% reduction in energy usage & 30% reduction in distance driven** on average.



## :x: Missing Features (Due to Time Constraints)
- Real data integration with **InfluxDB** for algorithm input
- Notifications from sensors *(sensor code is in a separate repository)*
- Ability to **modify**, **approve**, or **reject** routes

> **:information_source:Note:**  
> The simulated data used in our testing is too large to include in this repository.  
> To run the project with simulation data, you’ll need to generate or provide your own.

---

<img src="https://github.com/P2-Smart-Trash-Pickup/El-bil/blob/main/AI%20Garbage%20monkey.png" alt="AI Garbage Monkey" width="600"/>
