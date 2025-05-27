# Electric Trash pickup

Plan:
- We will run the server Using The Lora Protocol since we need to sent data a far and it is the ideal for that.
  It will go to a likely Self hosted Lora translation server, then be forwarded using JSON to our actual webserver.
- The Webserver is going to receive the JSOn files either from a POST request or more like a MQTT subscription.
- It then processes this data and spits out statistics and suggestions on the actual homepage.

Features:
- Route Suggestion
- Plotted Fill levels
- Login page

![AI Garbage Monkey](https://github.com/P2-Smart-Trash-Pickup/El-bil/blob/main/AI%20Garbage%20monkey.png)