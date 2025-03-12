import json

hej = open('derulo.json','r')

martin_dufter = hej.read()
hej.close()
p = json.loads(martin_dufter)
navn = input('navn: ')
alder = input('alder: ')
alder = int(alder)
p[navn] = alder
k = json.dumps(p)
hej = open('derulo.json','w')
hej.write(k)
hej.close()
#💅