#Laver par med input og rigtigt output
test = [[-5,"Value is negative"], 
        [-0.4,"Value is negative"], 
        [0,"Value is 0"], 
        [0.7,"Value is between zero and three"], 
        [1,"Value is between zero and three"], 
        [4,"Value is larger than 3 and smaller than 10"], 
        [3452,"Value is larger than or equal to 10"],
        [3,"Value is 3"]]

def checkInputValue(value):
    if value == 3:
        return "Value is 3"
    elif value == 0: 
        return "Value is 0"
    elif value>3:
        if (value<10):
            return "Value is larger than 3 and smaller than 10"
        else:
            return "Value is larger than or equal to 10"
    else:
        if value<0:
            return "Value is negative"
        else:
            return "Value is between zero and three"


for i in test:
    output = checkInputValue(i[0])
    #Sammenligner output med det rigtigt output
    if output == i[1]:
        print("Test succes")
    else:
        print("Test fail")
