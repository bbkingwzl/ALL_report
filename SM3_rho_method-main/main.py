import mySM3
import random

set1 = set()
flag =1
i = str(random.randint(0, 2 ** 512))
while(flag):
    i1 = mySM3.SM3(i,1)
    i2 = i1[0:8]
    if(i2 in set1):
        flag = 0
        print("True")
        print(i2)
    else:
        set1.add(i2)
    i = i1
print("end")
