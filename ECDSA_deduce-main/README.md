# ECDSA_deduce
本次实验以代码形式具体实现了ECDSA的deduce，本次实验为个人独自完成。引用部分在文中有所展示。
## 代码说明以及注意事项
除mathfunc导入外，还需要导入hashlib以及bitcoin库，在运行前需要先pip install hashlib以及pip install bitcoin  
在运行时直接下载py文件运行ecdsa_deduce即可。  
另外是本次代码上传时间为多天前，但由于需要重新上传至总库因此时间改变，具体实现时间为2022-7-23： 
![图片](https://user-images.githubusercontent.com/105708747/180752073-83a1fb83-3d20-4017-bc17-568bb257e183.png)

## 具体函数介绍
导入所需库后（mathfunc为笔者所编写的py文件），设置有限域的阶以及椭圆曲线的阶以及基本点,并利用mathfunc中的生成密钥函数进行密钥的生成工作。
```python
import mathfunc
from hashlib import sha256
import bitcoin

'''设置有限域的阶以及椭圆曲线的阶'''
P1 = 115792089237316195423570985008687907853269984665640564039457584007908834671663
P2 = 115792089237316195423570985008687907852837564279074904382605163141518161494337

X = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Y = 32670510020758816978083085130507043184471273380659243275938904335757337482424
basic_point = (X, Y)

private_key, public_key = mathfunc.generate_key()
```
利用生成的私钥对信息mes进行签名，这里使用的hash函数为sha256.在完成哈希后，需要生成一个随机数k，在生成随机数时，根据RFC6979，使用bitcoin库中的函数进行生成。而后利用该随机数k与基本点相乘得到一个随机点。
```python
def Sig(private_key, mes):
    res = []
    hash = int(sha256(mes.encode('utf-8')).hexdigest(),16)
    #生成随机数k，利用k与基本点相乘得到一个随机的点G
    k = bitcoin.main.deterministic_generate_k(hash,private_key)
    G = mathfunc.ECC_mul(k, basic_point)
    res.append(G[0] % P1)
    res.append(mathfunc.cal_inverse(k, P2) * (hash + res[0] * private_key) % P2)
    return res
mes = "1234567890"
sign = Sig(private_key, mes)
```
最后，根据签名内容反推出公钥，这里使用的椭圆曲线为y^2=x^3+7.根据签名内容生成G1、G2两个点，而后对消息进行哈希作为参照。这里可能的key的取值有两个，即利用G1、G2能够得到两个可能解这里以G1为例进行说明，将签名得到的sign[1]与上述生成的G1做乘法运算，再将哈希的结果与基本点做乘法运算，随后得到一个加数与mul1得到的结果相加，最终利用相加结果进行推断。
```python
'''根据签名内容反推出公钥：'''
def ecdsa_dedeuce(sign, mes):
    x = sign[0] % P1
    y=mathfunc.Tonelli_Shanks(((x**3)+7), P1)
    G1=(x,y)
    G2=(x, P1 - y)

    hash = int(sha256(mes.encode('utf-8')).hexdigest(),16)
    # key1_possible
    mul1=mathfunc.ECC_mul(sign[1] % P2, G1)#将签名得到的sign[1]与上述生成的G1做乘法运算
    mul2=mathfunc.ECC_mul(hash % P2, basic_point)#将哈希的结果与基本点做乘法运算
    add3=(mul2[0], P1 - mul2[1])
    add1=mathfunc.ECC_add(mul1, add3)
    key1_possible=mathfunc.ECC_mul(mathfunc.cal_inverse(sign[0], P2), add1)

    # key2_possible，与上述操作相似
    mul3=mathfunc.ECC_mul(sign[1] % P2, G2)
    add2=mathfunc.ECC_add(mul3, add3)
    key2_possible=mathfunc.ECC_mul(mathfunc.cal_inverse(sign[0], P2), add2)
    return key1_possible,key2_possible
key1_possible, key2_possible=ecdsa_dedeuce(sign, mes)
```
## 打印结果
对最终结果进行打印，最终结果如下：
![图片](https://user-images.githubusercontent.com/105708747/180432771-6395418e-220a-400b-8534-12756a566e50.png)
## mathfunc函数介绍
下面介绍mathfunc.py中的函数。首先设置有限域的阶以及椭圆曲线的阶以及基本点，以及椭圆曲线方程的参数a=0，b=7，则函数方程为y^2=x^3+7
```python
import secrets
'''设置有限域的阶以及椭圆曲线的阶'''
P1 = 115792089237316195423570985008687907853269984665640564039457584007908834671663
P2 = 115792089237316195423570985008687907852837564279074904382605163141518161494337
X = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Y = 32670510020758816978083085130507043184471273380659243275938904335757337482424
basic_point = (X, Y)

'''设置函数参数a=0，b=7，则函数方程为y^2=x^3+7'''
A = 0
B = 7
```
再构造ECDSA所需使用的数学函数，分别是利用扩展欧几里得算法求逆以及Tonelli-Shanks求解二次剩余，这里引用https://blog.csdn.net/qq_51999772/article/details/122642868
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
