
import selectors 
import socket 
import json
sel = selectors.DefaultSelector() 
def accept(sock, mask): 
    conn, addr = sock.accept() # Should be ready 
    print('accepted', conn, 'from', addr) 
    conn.setblocking(False) 
    sel.register(conn, selectors.EVENT_READ, read) 
def read(conn, mask): 
    
    data = conn.recv(1000).decode() # Should be ready 
    if data: 
        print('echoing', data, 'to', conn) 
        string_data = json.loads(data)
        hej = open('derulo.json','r')
        martin_dufter = hej.read()
        hej.close()
        p = json.loads(martin_dufter)
        p[string_data['navn']] = string_data['alder']
        k = json.dumps(p)
        hej = open('derulo.json','w')
        hej.write(k)
        hej.close()
        conn.send('josefine'.encode()) # Hope it won't block 
    else: 
        print('closing', conn) 
        sel.unregister(conn) 
        conn.close()

sock = socket.socket() 
sock.bind(('localhost', 1234)) 
sock.listen(100) 
sock.setblocking(False) 
sel.register(sock, selectors.EVENT_READ, accept) 
while True: 
    events = sel.select() 
    for key, mask in events: 
        callback = key.data 
        callback(key.fileobj, mask)