import mySM3
import random

for j in range(0,1000):
    count = 0
    for i in range(0,2**8):
        x = str(random.randint(0,2**512))
        y = str(random.randint(0,2**512))
        x1 = mySM3.SM3(x,0)
        y1 = mySM3.SM3(y,0)
        x2 = x1[0:4]
        y2 = y1[0:4]
        if(x2 == y2):
            print("True")
print("end")
