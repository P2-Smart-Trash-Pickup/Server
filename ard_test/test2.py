file = open("test.csv","r")
file2 = open("test2.csv","a+")

i = 0
for line in file:
    i += 1
    number = line.split(":")[1].strip()

    out_str = f"{i}, {number}\n"

    file2.write(out_str)
file.close()

file2.close()

