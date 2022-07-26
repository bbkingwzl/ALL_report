# SM2_2p_decrypt
implement sm2 2P decrypt with real network communication,本次实验为笔者独自完成。引用部分在文中有所展示。
## 运行解释以及注意事项
在导入所给py文件mathfunc以及sm3后，在运行时直接下载py文件运行sm2_2p_decrypt即可。
## sm2 2P decrypt实现
### 准备阶段
导入所需库后（mathfunc为笔者所编写），设置有限域的阶以及椭圆曲线的阶以及基本点,而后设置椭圆曲线相关参数a、b。sm3.py文件引用链接：https://blog.csdn.net/qq_33439662/article/details/121635423
```python
import mathfunc
import secrets
import math
from sm3 import sm3hash

'''设置有限域的阶以及椭圆曲线的阶'''
P1 = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
P2 = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
X = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
Y = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
G = (X, Y)

'''设置椭圆曲线参数'''
a = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93
```
定义KDF函数即密钥派生函数，这里引用https://blog.csdn.net/qq_33439662/article/details/122590298
```python
def KDF(z, klen):
    ct=1
    k=''
    for _ in range(math.ceil(klen/256)):
        k=k+sm3hash(hex(int(z+'{:032b}'.format(ct),2))[2:])
        ct=ct+1
    k='0'*((256-(len(bin(int(k,16))[2:])%256))%256)+bin(int(k,16))[2:]
    return k[:klen]
```
### (1)Generate sub private key d1、d2
在两方各自产生一个随机数d1、d2，并计算出public key P。原理为：  
![图片](https://user-images.githubusercontent.com/105708747/180911244-90f74f78-b73e-4cb4-b2da-f6977dea5aed.png)

```python
'''(1)Generate sub private key d1、d2'''
d1 = secrets.randbelow(P2-1)
d2 = secrets.randbelow(P2-1)
d1d2_ = mathfunc.cal_inverse(d1 * d2, P1)
P = mathfunc.ECC_mul(d1d2_ - 1, G)
print('Public key P:',P)
```
### (2)get ciphertext C
首先定义加密函数完成加密过程，原理如下：  
![图片](https://user-images.githubusercontent.com/105708747/180911740-6aa89b12-f048-48f4-83c2-ed663324c402.png)  
完成加密后将C1,C2,C3进行级联得到ciphertext C并进行打印，若C1不为0，则计算T1，并发送给另一方
```python
'''get ciphertext C'''
def Encryt(M):
    M= '0' * ((4 - (len(bin(int(M.encode().hex(), 16))[2:]) % 4)) % 4) + bin(int(M.encode().hex(), 16))[2:]
    klen = len(M)
    k = secrets.randbelow(P2-1)
    C1 =mathfunc.ECC_mul(k,G)
    [x2,y2] = mathfunc.ECC_mul(k,P)
    x2, y2 = '{:0256b}'.format(x2), '{:0256b}'.format(y2)
    x2_y2 = x2+y2
    t = KDF(x2_y2,klen)
    C2 = ((klen//4)-len(hex(int(M,2)^int(t,2))[2:]))*'0'+hex(int(M,2)^int(t,2))[2:]
    C3_ = x2+M+y2
    C3 = sm3hash(hex(int(C3_,2))[2:])
    return [C1,C2,C3]
    
M = 'author is bbkingwzl'
[C1,C2,C3] = Encryt(M)
C = str(C1[0])+str(C1[1])+C2+C3
print('计算得到的ciphertext C:',C)
if(C1 != 0):
    d1_ = mathfunc.cal_inverse(d1,P1)
    T1 = mathfunc.ECC_mul(d1_,C1)
    print("计算得到的T1：",T1)
```
### (3) compute T2
在另一方接收到T1后，开始计算T2，并将T2发送至密文获取方原理如下：  
![图片](https://user-images.githubusercontent.com/105708747/180912188-d43f20e8-c14f-4593-af26-41da6b0133d9.png)

```python
'''(3) compute T2'''
d2_ = mathfunc.cal_inverse(d2,P1)
T2 = mathfunc.ECC_mul(d2_,T1)
print("计算得到的T2：",T2)
```
### (4) Recover plaintext M_
在密文获取方接收到T2后便可以开始恢复明文M''，原理如下：  
![图片](https://user-images.githubusercontent.com/105708747/180912478-65bbb1b8-52ff-4185-9519-fb5ff60a09db.png)
```python
'''Recover plaintext M_'''
def decypt(C1,C2,C3):
    klen = len(C2)*4
    kP = mathfunc.ECC_mul(d1d2_-1,C1)
    [x2,y2] = kP
    x2, y2 = '{:0256b}'.format(x2), '{:0256b}'.format(y2)
    x2_y2 = x2+y2
    t = KDF(x2_y2,klen)
    M__ = '0' * (klen - len(bin(int(C2, 16) ^ int(t, 2))[2:])) + bin(int(C2, 16) ^ int(t, 2))[2:]
    u_ = x2+M__+y2
    u = sm3hash(hex(int(u_,2))[2:])
    if(u == C3):
        M__ = hex(int(M__,2))[2:]
        M__ =str(bytes.fromhex(M__))
        M__ = '\n'.join(M__[2:-1].split('\\n'))
        print("最终解密得到的M‘’为：",M__)
        print("M与M''是否相等：", M == M__)
decypt(C1,C2,C3)
```
## 打印结果展示
![图片](https://user-images.githubusercontent.com/105708747/180912536-8847740f-14b9-4a5e-bd7d-ad15f6bbdd79.png)
## mathfunc函数介绍
下面介绍mathfunc.py中的函数。首先设置有限域的阶以及椭圆曲线的阶以及基本点，以及椭圆曲线方程的参数
```python
import secrets
'''设置有限域的阶以及椭圆曲线的阶'''
P1 = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
P2 = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
X = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
Y = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
basic_point = (X, Y)

'''设置椭圆曲线参数'''
A = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
B = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93
```
再构造SM2所需使用的数学函数，分别是利用扩展欧几里得算法求逆以及Tonelli-Shanks求解二次剩余,这里引用https://blog.csdn.net/qq_51999772/article/details/122642868
```python
'''利用扩展欧几里得算法求逆'''
def cal_inverse(a, b):
    #若相等则直接返回
    if a == b:
        return (a, 1, 0)

    else:
        flag = False
        c = [a]
        d = [b]
        e = []
        res = []

        #循环判断直到res为0
        i = 0
        while not (flag):
            e.append(d[i]//c[i])
            res.append(d[i]%c[i])
            d.append(c[i])
            c.append(res[i])
            i += 1
            if res[i-1] == 0:
                flag = True

        #res3为公因子，res1、res2为系数
        i -= 1
        res1 = [1]
        res2 = [0]
        res3 = c[i]

        i -= 1
        num = i
        while i >= 0:
            res2.append(res1[num-i])
            res1.append(res2[num-i] - e[i]*res1[num-i])
            i -= 1

    if(res3 == 1):
        return res1[-1] % b
    else:
        return -1


'''Tonelli-Shanks求解二次剩余'''
def Tonelli_Shanks(y,p):
    '''这里判断是否为二次剩余，即利用勒让德符号进行判断'''
    assert pow(y,(p - 1) // 2,p) == 1
    if p % 4 == 3:
        return pow(y,(p + 1) // 4,p)
    q = p - 1
    s = 0
    while q % 2 == 0:
        q = q // 2
        s += 1
    for z in range(2,p):
        if pow(z,(p - 1) // 2,p) == p - 1:
            c = pow(z,q,p)
            break
    r = pow(y,(q + 1) // 2,p)
    t = pow(y,q,p)
    m = s
    if t % p == 1:
        return r
    else:
        i = 0
        while t % p != 1: # 外层循环的判断条件
            temp = pow(t,2**(i+1),p)
            i += 1
            if temp % p == 1:
                b = pow(c,2**(m - i - 1),p)
                r = r * b % p
                c = b * b % p
                t = t * c % p
                m = i
                i = 0 # 每次内层循环结束后i值要更新为0
        return r
```
利用上述函数定义椭圆曲线上的加法运算以及乘法运算，在加法运算中包括斜率存在以及斜率不存在利用微分求解两种情况
```python
'''编写椭圆曲线加法与乘法运算'''
def ECC_add(a, b):

    #首先考虑是否存在0的情况
    if(a == 0 and b == 0):
        return 0
    if(a==0):
        return b
    if(b==0):
        return a

    if(a == b):
        #此时无法直接求斜率，需要借助微分
        k = (3 * a[0] ** 2 + A) * cal_inverse(2 * a[1], P1) % P1
        res = (k**2 - 2*a[0]) % P1
        return(res,(k*(a[0] - res) - a[1]) % P1)

    else:
        #保证大数在前
        if a[0] > b[0]:
            temp = a
            a = b
            b = temp
        #计算斜率
        k = (b[1] - a[1]) * cal_inverse(b[0] - a[0], P1) % P1

        #依据椭圆曲线的计算规则进行计算
        res = (k ** 2 - a[0] - b[0]) % P1
        return (res,(k * (a[0] - res) - a[1]) % P1)


def ECC_mul(a, b):

    res = 0#初始化res为无穷远点O
    a_2 = bin(a)[2:]#将a转为二进制
    b_temp = b


    for i in reversed(range(len(a_2))):
        if a_2[i] == '1':
            res = ECC_add(res, b_temp)
        b_temp = ECC_add(b_temp,b_temp)

    return res
```
利用python的secret库生成私钥以及公钥
```python
def generate_key():
    private_key = int(secrets.token_hex(32), 16)
    public_key = ECC_mul(private_key, basic_point)
    return private_key, public_key
```

