# SM3_Birthday_Attack
本次实验以代码形式具体实现了SM3的生日攻击，本次实验为笔者独自完成。引用部分在文中有所展示。
## 代码说明以及注意事项
导入mySM3后，在运行时直接下载py文件运行birthday即可。
另外是本次代码上传时间为多天前，但由于需要重新上传至总库因此时间改变，具体实现时间为2022-7-8： 
![图片](https://user-images.githubusercontent.com/105708747/180755146-aa0013e0-c60a-4434-a570-491989295e9b.png)
## 原理介绍
两个不同的输入，经过哈希算法后，得到了同样的哈希值，就叫做哈希碰撞。由于通常的哈希算法中，哈希值的空间远小于输入的空间，这就意味着信息熵有丢失。一个空间较大的集合(输入)通过哈希算法映射到一个空间较小的集合(哈希值)，必然会造成多个输入映射到一个哈希值上，这就是所谓的哈希碰撞。这就是说当输入的可能性被完全枚举时，一定会产生哈希碰撞。这里引用https://blog.csdn.net/weixin_43749051/article/details/104206696?ops_request_misc=%257B%2522request%255Fid%2522%253A%2522165874600316781790796861%2522%252C%2522scm%2522%253A%252220140713.130102334..%2522%257D&request_id=165874600316781790796861&biz_id=0&utm_medium=distribute.pc_search_result.none-task-blog-2~all~sobaiduend~default-1-104206696-null-null.142^v33^control,185^v2^control&utm_term=%E7%94%9F%E6%97%A5%E6%94%BB%E5%87%BB%E5%8E%9F%E7%90%86&spm=1018.2226.3001.4187
## 具体实现
这里取SM3hash输出的前16位为例进行实现,由于生日碰撞为一个概率事件，本次实验通过重复1000次来观察成功次数。根据生日悖论，内层循环至少需要重复2^8次才能够以大概率找到一个成功的碰撞。在内层循环中，每次产生两个随机数作为SM3的输入，经过SM3加密后，对比其16进制的前4位即二进制的前16位，若相等则输出True。代码如下：
```python
import mySM3
import random

for j in range(0,1000):
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
```
ps:1.此处使用的SM3加密函数已提前写好，因此不做介绍
## 打印结果展示
![图片](https://user-images.githubusercontent.com/105708747/180758961-fd36dd14-017b-48db-bd2c-f0364d8f27a2.png)

