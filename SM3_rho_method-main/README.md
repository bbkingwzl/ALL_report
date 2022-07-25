# SM3_rho_method
此处以SM3的hash输出的前64位为例进行碰撞，因为并没有找到合适的生成表达式，因此直接使用python中的随机数进行碰撞。本次实验为笔者独自完成。引用部分在文中有所展示。
## 运行解释以及注意事项
首先创建一个集合来存放之前随机生成的随机数经过SM3加密后得到的hash结果，并设置一个flag用以反复循环。
```python
import mySM3
import random

set1 = set()
flag =1

```
通过不断循环往复，每次循环生成一个随机数作为SM3的输入，截取其十六进制的前16位即二进制的前64位，将该结果与集合中已存在元素进行对比，若已存在于其中那么便是成功找到一个碰撞，返回True。若不存在于集合之中，则需要将其放入集合之中，继续执行循环判断。
```python

while(flag):
    i = str(random.randint(0,2**512))
    i1 = mySM3.SM3(i,0)
    i2 = i1[0:16]
    if(i2 in set1):
        flag = 0
        print("True")
        print(i2)
    else:
        set1.add(i2)
print("end")
```
