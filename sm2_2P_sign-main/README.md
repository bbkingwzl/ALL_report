# sm2_2P_sign
implement sm2 2P sign with real network communication,具体实验报告见readme
## sm2 2P sign实现
### 准备阶段
导入所需库后（mymathfunc为笔者所编写的py文件），设置有限域的阶以及椭圆曲线的阶以及基本点,而后设置椭圆曲线相关参数a、b。并利用mathfunc中的密钥生成函数生成公私钥对。
```python
import secrets
from gmssl import sm3, func
import mymathfunc

'''设置有限域的阶以及椭圆曲线的阶'''
P1 = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
P2 = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
X = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
Y = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
basic_point = (X, Y)

'''设置椭圆曲线参数'''
a = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93

sk, pk = mymathfunc.generate_key()
```
首先定义计算ZA的函数用以计算ZA,其传递的参数依次是：ID，椭圆曲线参数a、b,G点x、y,公钥x、y。在拼接完毕后使用sm3算法对其进行哈希。
```python
def cal_ZA(ID, a, b, X, Y, sk, pk):

    ENTL=str(len(ID.encode()) << 3)

    joint= ENTL + ID + str(a) + str(b) + str(X) + str(Y) + str(sk) + str(pk)
    joint_bytes=bytes(joint,encoding='utf-8')
    hash= sm3.sm3_hash(func.bytes_to_list(joint_bytes))
    return int(hash, 16)
```
### (1)Generate sub private key d1、d2,and compute p1
在两方均需各自生成一个随机数定义为d1、d2，在发送端计算P1 = d1^(-1)*G,将P1发送至接收方。其流程如下：  
![图片](https://user-images.githubusercontent.com/105708747/180678418-87750104-50d7-4756-8f4c-1ab3e2c8c955.png)
![图片](https://user-images.githubusercontent.com/105708747/180678523-70026f55-55bf-4cc1-99fd-12decef99bef.png)
```python
if __name__ == '__main__':

    '''(1)Generate sub private key d1、d2,and compute p1'''
    d1 = secrets.randbelow(P2-1)
    d1_inverse = mymathfunc.cal_inverse(d1,P2)
    d2 = secrets.randbelow(P2-1)
    d2_inverse = mymathfunc.cal_inverse(d2,P2)
    p1 = mymathfunc.ECC_mul(d1_inverse,basic_point)
    print("d1=",d1)
    print("d2=",d2)
    print("P1=", p1)
```
### (2)Generate shared public key P
在接受方生成随机数d2后，计算P = d2^(-1)*P1-G.P为公钥，需要进行公布，其流程如下：  
![图片](https://user-images.githubusercontent.com/105708747/180679393-8faa91c4-3251-4cf1-b248-f71d0f8fa996.png)
```python
    '''(2)Generate shared public key P'''
    _P = mymathfunc.ECC_mul(d2_inverse,p1)
    G_inverse = [X, -Y]
    P = mymathfunc.ECC_add(_P,G_inverse)
    print("P=", P)
```
### (3)Set Z to be identifier for both parties,message is M and calculate e,Q1
在发送方，利用在准备阶段定义的cal_ZA函数计算ZA，并将其级联M进行哈希得到e。随机生成随机数k1，计算Q1=k1G。将Q1、e发送至接收方。流程如下：  
![图片](https://user-images.githubusercontent.com/105708747/180679651-d2dd0de4-8420-41b6-9e60-6d9a6215f82c.png)
```python
    '''(3)Set Z to be identifier for both parties,message is M and calculate e,Q1'''
    ID1 = "bbkingwzl"
    Z_A = cal_ZA(ID1, a, b, X, Y, sk, pk)
    M = b'lzwgnikbb'
    _M = b''.join([mymathfunc.to_byte(i) for i in [Z_A,M]])
    print("bbkingwzl发送的消息为：",M)
    e = int.from_bytes(mymathfunc.to_byte(sm3.sm3_hash(func.bytes_to_list(_M))), byteorder='big')
    k1 = secrets.randbelow(P2-1)
    Q1 = mymathfunc.ECC_mul(k1,basic_point)
    print("e=", e)
    print("Q1=", Q1)
```
### (4)Generate partial signature r
在接收方随机生成两个随机数k2、k3，计算Q2=k2G，并利用Q2（x1，y1）=k3Q1+Q2。在x1后与e相加得到r，最后计算s2=d2k3,s3=d2(r+k2).最终将r，s2，s3发送至发送方流程如下：  
![图片](https://user-images.githubusercontent.com/105708747/180680028-2c9a0c11-212d-42f0-9991-b478c6f17ad5.png)
```python
    '''(4)Generate partial signature r'''
    k2 = secrets.randbelow(P2-1)
    Q2 = mymathfunc.ECC_mul(k2,basic_point)
    k3 = secrets.randbelow(P2-1)
    k3Q1 = mymathfunc.ECC_mul(k3,Q1)
    k3Q1_plus_Q2 = mymathfunc.ECC_add(k3Q1,Q2)
    r = (k3Q1_plus_Q2[0]+e) % P2
    print("r=", r)
    s2 = (d2*k3) % P2
    s3 = (d2*(r+k2)) % P2
    print("s2=", s2)
    print("s3=", s3)
```
### (5)Generate signature sigma=(r,s)
在发送方接收到r，s2，s3后，计算s=（d1*k1）*s2+d1*s3-r,随后判断其是否不等于零以及是否不等于n-r。最终输出（r，s）。流程如下：  
![图片](https://user-images.githubusercontent.com/105708747/180680258-2bf5eb92-d406-49ff-90bd-8a551e6f484d.png)
```python
    '''(5)Generate signature sigma=(r,s)'''
    s = (d1 * k1 * s2 + d1 * s3 - r ) % P2
    if s != 0 and s != P2 - r:
        print("s=", s)
```
### 运行结果展示
![图片](https://user-images.githubusercontent.com/105708747/180680316-19f7dfef-d2be-4a89-a453-94a81ea8f318.png)
### 总体流程以及总体代码展示
![图片](https://user-images.githubusercontent.com/105708747/180680339-3a675633-c3f3-4861-a883-7c484e20da2a.png)
```python
if __name__ == '__main__':

    '''(1)Generate sub private key d1、d2,and compute p1'''
    d1 = secrets.randbelow(P2-1)
    d1_inverse = mymathfunc.cal_inverse(d1,P2)
    d2 = secrets.randbelow(P2-1)
    d2_inverse = mymathfunc.cal_inverse(d2,P2)
    p1 = mymathfunc.ECC_mul(d1_inverse,basic_point)
    print("d1=",d1)
    print("d2=",d2)
    print("P1=", p1)

    '''(2)Generate shared public key P'''
    _P = mymathfunc.ECC_mul(d2_inverse,p1)
    G_inverse = [X, -Y]
    P = mymathfunc.ECC_add(_P,G_inverse)
    print("P=", P)

    '''(3)Set Z to be identifier for both parties,message is M and calculate e,Q1'''
    ID1 = "bbkingwzl"
    Z_A = cal_ZA(ID1, a, b, X, Y, sk, pk)
    M = b'lzwgnikbb'
    _M = b''.join([mymathfunc.to_byte(i) for i in [Z_A,M]])
    print("bbkingwzl发送的消息为：",M)
    e = int.from_bytes(mymathfunc.to_byte(sm3.sm3_hash(func.bytes_to_list(_M))), byteorder='big')
    k1 = secrets.randbelow(P2-1)
    Q1 = mymathfunc.ECC_mul(k1,basic_point)
    print("e=", e)
    print("Q1=", Q1)

    '''(4)Generate partial signature r'''
    k2 = secrets.randbelow(P2-1)
    Q2 = mymathfunc.ECC_mul(k2,basic_point)
    k3 = secrets.randbelow(P2-1)
    k3Q1 = mymathfunc.ECC_mul(k3,Q1)
    k3Q1_plus_Q2 = mymathfunc.ECC_add(k3Q1,Q2)
    r = (k3Q1_plus_Q2[0]+e) % P2
    print("r=", r)
    s2 = (d2*k3) % P2
    s3 = (d2*(r+k2)) % P2
    print("s2=", s2)
    print("s3=", s3)

    '''(5)Generate signature sigma=(r,s)'''
    s = (d1 * k1 * s2 + d1 * s3 - r ) % P2
    if s != 0 and s != P2 - r:
        print("s=", s)
```
## mymathfunc函数介绍
下面介绍mymathfunc.py中的函数。首先设置有限域的阶以及椭圆曲线的阶以及基本点，以及椭圆曲线方程的参数
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
将变量转换为bytes类型的函数，这里引用https://blog.csdn.net/qq_43339242/article/details/123221091
```python
# 转换为bytes，第二参数为字节数（可不填）
def to_byte(x, size=None):
    if isinstance(x, int):
        if size is None:  # 计算合适的字节数
            size = 0
            tmp = x >> 64
            while tmp:
                size += 8
                tmp >>= 64
            tmp = x >> (size << 3)
            while tmp:
                size += 1
                tmp >>= 8
        elif x >> (size << 3):  # 指定的字节数不够则截取低位
            x &= (1 << (size << 3)) - 1
        return x.to_bytes(size, byteorder='big')
    elif isinstance(x, str):
        x = x.encode()
        if size != None and len(x) > size:  # 超过指定长度
            x = x[:size]  # 截取左侧字符
        return x
    elif isinstance(x, bytes):
        if size != None and len(x) > size:  # 超过指定长度
            x = x[:size]  # 截取左侧字节
        return x
    elif isinstance(x, tuple) and len(x) == 2 and type(x[0]) == type(x[1]) == int:
        # 针对坐标形式(x, y)
        return to_byte(x[0], size) + to_byte(x[1], size)
    return bytes(x)
```
