# SM3_Birthday_Attack
这里取SM3hash输出的前32位为例进行实现,由于生日碰撞为一个概率事件，本次实验通过重复1000次来观察成功次数。根据生日悖论，内层循环至少需要重复2^16次才能够以大概率找到一个成功的碰撞。在内层循环中，每次产生两个随机数作为SM3的输入，经过SM3加密后，对比其16进制的前8位即二进制的前32位，若相等则输出True。代码如下：
```python
import mySM3
import random

for j in range(0,1000):
    for i in range(0,2**16):
        x = str(random.randint(0,2**512))
        y = str(random.randint(0,2**512))
        x1 = mySM3.SM3(x,0)
        y1 = mySM3.SM3(y,0)
        x2 = x1[0:8]
        y2 = y1[0:8]
        if(x2 == y2):
            print("True")
print("end")
```
ps:1.此处使用的SM3加密函数已提前写好，因此不做介绍
  2.此处代码与文件中有所不同，以readme中所示为准