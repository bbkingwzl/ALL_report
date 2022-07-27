# SM3_rho_method
此处以SM3的hash输出的前64位为例进行碰撞，因为并没有找到合适的生成表达式，因此直接使用python中的随机数进行碰撞。本次实验为笔者独自完成。引用部分在文中有所展示。

## 运行解释以及注意事项
导入所提供文件的mySM3后直接运行main.py文件即可。
另外是本次代码上传时间为多天前，但由于需要重新上传至总库因此时间改变，具体实现时间为2022-7-17： 
![图片](https://user-images.githubusercontent.com/105708747/181281111-924bfb71-5fa2-487a-a3e3-63b876589f6a.png)
## Rho method攻击的具体实现
首先创建一个集合来存放之前随机生成的随机数经过SM3加密后得到的hash结果，并设置一个flag用以反复循环。在初始时生成一个随机数i。
```python
import mySM3
import random

set1 = set()
flag =1
i = str(random.randint(0, 2 ** 512))
```
通过不断循环往复，这里每次需要生成一个新的哈希结果，我选择的是将上一次的哈希结果再次进行哈希，以此产生下一个需要哈希的取值，截取其十六进制的前8位即二进制的前32位，将该结果与集合中已存在元素进行对比，若已存在于其中那么便是成功找到一个碰撞，返回True。若不存在于集合之中，则需要将其放入集合之中，继续执行循环判断。
```python
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
```
## 打印结果展示
![图片](https://user-images.githubusercontent.com/105708747/181281530-6eb1ca6e-dd7f-41c1-a3ea-e98bfceae1b7.png)
