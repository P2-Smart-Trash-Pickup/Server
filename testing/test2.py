def bubbleSort(arr):
    n = len(arr)
    swapped = True
    for i in range(n-1):
        for j in range( n-i-1):
 
            if arr[j +1 ] < arr[j]:
                swapped = False
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
         
        if swapped:
            return

#Laver test par af input og forventet output. 
tests = [[[5,3,1,2],[1,2,3,5]],
         [[],[]],
         [[1,2,3,4],[1,2,3,4]],
         [[-5,1,5,2],[-5,1,2,5]]]

for test in tests:
    bubbleSort(test[0])
    #Sammenligner input og forventet output.
    if test[0] == test[1]:
        print("Test succes")
    else:
        print("Test failed")

