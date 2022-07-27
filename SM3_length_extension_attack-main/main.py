import mySM3
import random

"""假设M = M1||M2，M1与M2值如下但未知"""
M1 = str(random.randint(0,2**512))
M2 = str(random.randint(0,2**512))
M = M1+M2

hash1 = mySM3.SM3(M,1)
hash1_temp = int(hash1,16)

"""构造M3，假设M3原消息长度为24bit，其十六进制表示为616263"""
M3_temp = "616263"
"""填充M3，最后64bit表示M3的长度为24即"""
str1 = "00000000 00000018"
"""继续填充，首先在M3后面填充bit1，而后剩余的423bit均为0即"""
str2 = "8000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"

M3 = M3_temp + str2 + str1

M3_byte = mySM3.str_2_byte(M3)

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

print("经过长度扩展后得到的哈希结果：",hash2)
"""验证，若直接加密M1||M2||M3得到结果与上述不同，这是因为其中间存在padding，实际上应为M1||M2||padding||M3"""
M4 = M1+M2+M3
hash4 = mySM3.SM3(M4,1)
print("验证直接对M1||M2||M3进行哈希得到的结果：",hash4)
print("两哈希值是否相等：",hash2 == hash4)
