def mySqrt(number, guess, step, tol):
    while True:
        if (number<0):
            return -1 

        #Hvis at gæt er 0 anses der for der ikke er noget gæt, så den vælger et muligt gæt
        #Den checker egentligt om tallet er et komma tal.
        if (guess==0):
            if (number<1):        
                guess= 0.5*number
            else:
                guess= number*2	  
        
        #Ser hvis at gættet i anden lægger omkring det rigtigt tal. Hvis så må det være kvadratroden af tallet
        tmp = guess*guess		  
        if (abs((tmp-number))<=tol):	  
            return guess
        else:
            #Hvis at det gættet tal i anden er mindre en det reele må gættet være større, ellers må det være mindre.
            if (tmp<number):	  
                guess = step+guess
            else:				  
                guess = guess-step

tol = 0.001
#Første tal input, andet tal kvadrat roden af tallet. For minus tal er andet tal -1
test_vals = [[-4,-1], 
             [0,0], 
             [0.5,0.5**0.5], 
             [1,1**0.5], 
             [3,3**0.5], 
             [9,9**0.5], 
             [34,34**0.5]]

for i in test_vals:
    sqr_val = mySqrt(i[0],0,0.001, tol)

    #Checker hvis at output er ligemed kvadratroden af tallet +-tolerance
    if sqr_val >= i[1] - tol and sqr_val <= i[1] + tol :
        print("Succes")
    else:
        print("Failed")
