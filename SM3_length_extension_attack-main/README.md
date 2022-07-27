# SM3_length_extension_attack
本次实验以代码形式具体实现了SM3的长度扩展攻击，本次实验为笔者独自完成。引用部分在文中有所展示。
## 运行解释以及注意事项
导入所提供文件的mySM3后直接运行main.py文件即可。  
另外是本次代码上传时间为多天前，但由于需要重新上传至总库因此时间改变，具体实现时间为2022-7-18： 
![图片](https://user-images.githubusercontent.com/105708747/181272609-db942b39-9e4a-4046-81ad-2bd30289ae54.png)
## 长度扩展攻击的具体实现
首先计算得到M1||M2的哈希值，而后构造消息M3并根据规则进行填充。将hash（M1||M2）与M3作为输入经过CF，得到的结果即为长度扩展攻击得到的hash结果。在进行完上述过程后，我将其与直接哈希M1||M2||M3进行对比，发现结果不同。这是因为在第一种情况下，实际哈希为M1||M2||padding||M3，得到的结果与直接哈希M1||M2||M3不同。  
首先随机生成消息M1、M2，将其相加作为M，利用SM3对M进行哈希并转为整型。
```python
import mySM3
import random

"""假设M = M1||M2，M1与M2值如下但未知"""
M1 = str(random.randint(0,2**512))
M2 = str(random.randint(0,2**512))
M = M1+M2

hash1 = mySM3.SM3(M,0)
hash1_temp = int(hash1,16)

```
而后构造M3，假设M3原消息长度为24bit，其十六进制表示为616263。对M3进行填充，填充M3，最后64bit表示M3的长度为24；继续填充，首先在M3后面填充bit1，而后剩余的423bit均为0。最后将各部分拼接即可。最终将其按照byte进行分组，这是为了方便SM3加密算法。
```python
"""构造M3，假设M3原消息长度为24bit，其十六进制表示为616263"""
M3_temp = "616263"
"""填充M3，最后64bit表示M3的长度为24"""
str1 = "00000000 00000018"
"""继续填充，首先在M3后面填充bit1，而后剩余的423bit均为0即"""
str2 = "8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

M3 = M3_temp + str2 + str1

M3_byte = mySM3.str_2_byte(M3)
```
hash1中存储对M的哈希结果，即对M1||M2的哈希结果。将hash1与填充后的M3作为压缩函数CF的输入进行压缩，得到哈希结果为hash2.此时便实现了长度扩展攻击。
```python
arr = []
for i in range(0, 8):
    arr.append(0)
    arr[i] = (hash1_temp >> ((7 - i) * 32)) & 0xFFFFFFFF
iv1 = arr

def hash_val(msg):
    length = len(msg)
    reserve_val = length % 64
    msg.append(0x80)
    reserve_val = reserve_val + 1
    const = 56
    if reserve_val > const:
        const = const + 64

    for i in range(reserve_val, const):
        msg.append(0x00)

    length2 = (length) * 8
    length3 = [length2 % 0x100]
    for i in range(7):
        length2 = int(length2 / 0x100)
        length3.append(length2 % 0x100)
    for i in range(8):
        msg.append(length3[7 - i])

    group_num = round(len(msg) / 64)

    B = []
    for i in range(0, group_num):
        B.append(msg[i * 64:(i + 1) * 64])

    V = []
    V.append(iv1)
    for i in range(0, group_num):
        V.append(mySM3.CF(V[i], B[i]))

    y = V[i + 1]
    result = ""
    for i in y:
        result = '%s%08x' % (result, i)
    return result

hash2 = hash_val(M3_byte)

print(hash2)
```
值得注意的是，在代码中我对结果进行了对比。即直接将M1||M2||M3级联进行哈希结果发现与hash2不同，这是因为其中间存在padding，实际上应为M1||M2||padding||M3。
```python
"""验证，若直接加密M1||M2||M3得到结果与上述不同，这是因为其中间存在padding，实际上应为M1||M2||padding||M3"""
M4 = M1+M2+M3
hash4 = mySM3.SM3(M4,1)
print(hash4)
```
## 打印结果展示
![图片](https://user-images.githubusercontent.com/105708747/181276966-82fa791d-45c7-4daa-8aa8-d67c2541dc96.png)
