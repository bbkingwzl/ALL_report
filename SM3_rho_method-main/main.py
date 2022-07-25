import mySM3
import random

set1 = set()
flag =1

while(flag):
    i = str(random.randint(0,2**256))
    i1 = mySM3.SM3(i,0)
    i2 = i1[0:16]
    if(i2 in set1):
        flag = 0
        print("True")
        print(i2)
    else:
        set1.add(i2)
print("end")
