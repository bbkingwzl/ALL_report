# pitfalls_verify
verify the above pitfalls with proof-of-concept code 本次实验为笔者独自完成。引用部分在文中有所展示。
## 运行解释以及注意事项
在导入所给py文件mathfunc后，在运行时直接下载py文件运行pitfalls_verify即可。
## pitfalls_verify实现
### 准备阶段
导入所需库后（mathfunc为笔者所编写），设置有限域的阶以及椭圆曲线的阶以及基本点,而后设置椭圆曲线相关参数a、b。并利用mathfunc中的函数生成公私钥对。
```python
import mathfunc
import secrets
from hashlib import sha256

'''设置有限域的阶以及椭圆曲线的阶'''
P = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
N = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
X = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
Y = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
G = (X, Y)

'''设置椭圆曲线参数'''
A = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
B = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93

'''生成公私钥对'''
sk,pk = mathfunc.generate_key()
```
定义ecdsa签名函数，此处由于之前在做edcsa_deduce时已经编写过一次签名函数，因此此处不做解释并且直接使用。代码如下：
```python
'''利用私钥进行签名'''
def Sig(private_key, mes,k):
    res = []
    hash = int(sha256(mes.encode('utf-8')).hexdigest(),16)
    G1 = mathfunc.ECC_mul(k, G)
    res.append(G1[0] % P)
    res.append(mathfunc.cal_inverse(k, N) * (hash + res[0] * private_key) % N)
    return res
```
定义验证函数verify_with_m，此处的验证需要check m，其传入参数为明文消息以及签名结果r、s和所使用的公钥pk，代码实现如下：
```python
'''verification check m'''
def verify_with_m(mes,r,s,pk):
    e = int(sha256(mes.encode('utf-8')).hexdigest(),16)
    s_ = mathfunc.cal_inverse(s, N) % N
    es_ = e*s_ % N
    rs_ = r*s_ % N
    g1 = mathfunc.ECC_mul(es_,G)
    g2 = mathfunc.ECC_mul(rs_,pk)
    g = mathfunc.ECC_add(g1,g2)
    [x,y] = g
    if(x == r):
        print("pass verify")
        return True
    else:
        print("unpass verify")
        return False
```
最后，定义另一个验证函数verify_without_m，此处的验证不需要check m，其传入参数为一个哈希值e，以及签名结果r、s和所使用的的公钥pk，代码实现如下：
```python
'''verification does not check m'''
def verify_without_m(e,r,s,pk):
    s_ = mathfunc.cal_inverse(s, N) % N
    es_ = e*s_ % N
    rs_ = r*s_ % N
    g1 = mathfunc.ECC_mul(es_,G)
    g2 = mathfunc.ECC_mul(rs_,pk)
    g = mathfunc.ECC_add(g1, g2)
    [x, y] = g
    if(x == r):
        print("pass verify")
        return True
    else:
        print("unpass verify")
        return False
```
### Leaking k leads to leaking of d
此处实现泄露k导致密钥d泄露的计算过程，e为使用sha256进行哈希的消息值，而后泄露k即k已知，通过如下代码实现解出私钥d:
```python
''' Leaking k leads to leaking of d'''
def Leaking_k(mes,r,s):
    e = int(sha256(mes.encode('utf-8')).hexdigest(), 16)
    r_ = mathfunc.cal_inverse(r, N) % N
    d = r_*(k*s-e) % N
    print("(1)pitfalls1:Leaking k leads to leaking of d ")
    print("d:",d)
```
### Reusing k leads to leaking of d
此处实现重用k导致密钥d泄露的计算过程，两次前面得到r1，s1与r2，s2使用相同的私钥以及k。传入参数为用户使用的私钥以及两次加密的明文消息，而后通过如下代码实现在重用k的情况下计算得到k的过程：
```python
''' Reusing k leads to leaking of d'''
def Reuseing_k(sk1, mes1, mes2):
    print("(2)Reusing k leads to leaking of d")
    [r1,s1] = Sig(sk1, mes1,k)
    [r2,s2] = Sig(sk1,mes2,k)
    print('签名时使用的私钥d:',sk1)

    e1 = int(sha256(mes1.encode('utf-8')).hexdigest(),16)
    e2 = int(sha256(mes2.encode('utf-8')).hexdigest(),16)
    se = s1*e2 - s2*e1
    sr1 = s2*r1-s1*r2 % N
    sr1_ = mathfunc.cal_inverse(sr1,N)
    d = (se *sr1_) % N
    print('在重复使用k后计算出泄露的私钥d‘=',d)
    print('泄露出的私钥d‘与签名所使用的的d是否相等：',d == sk1)
```
### Two users, using k leads to leaking of d, that is they can deduce each other’s d
此处实现两个用户，即使用两个不同的私钥，在使用相同k的情况下依然会导致私钥d泄露的情况。传入参数为两个用户使用的私钥，以及两个用户各自加密的明文消息。具体实现如下：
```pyhthon
'''Two users, using k leads to leaking of d, that is they can deduce each other’s d'''
def reusing_k_by_2(sk11,sk22,mes11, mes22):
    [r,s11] = Sig(sk11,mes11,k)
    [r,s22] = Sig(sk22,mes22,k)
    print("(3)Two users, using k leads to leaking of d, that is they can deduce each other’s d")
    print("user1使用的私钥d1：",sk11)
    print("user2使用的私钥d2：",sk22)
    e11 = int(sha256(mes11.encode('utf-8')).hexdigest(),16)
    e22 = int(sha256(mes22.encode('utf-8')).hexdigest(),16)
    se = s22*e11 - s11*e22 +(s22 * r * sk11)
    sr1 = (s11*r) % N
    sr1_ = mathfunc.cal_inverse(sr1,N)
    d = (se *sr1_) % N
    print('user1通过计算得出的user2使用的私钥d2’：',d)

    se_ = s11*e22 - s22*e11 +(s11 * r * sk22)
    sr2 = (s22*r) % N
    sr2_ = mathfunc.cal_inverse(sr2,N)
    d_ = (se_ * sr2_) % N
    print('user1通过计算得出的user2使用的私钥d1',d_)
    print('user1与user2计算是否正确：',(d == sk22 and d_ == sk11))
```
### Malleability, e.g. (r,s) and (r,-s)are both valid signatures, lead to blockchain network split
这里实现若签名（r，s）与前面为（r,-s）那么这两个签名均为合法签名。这里需要传入的参数为明文消息，并且需要借助准备阶段实现的verify_with_m。具体实现如下：
```python
'''Malleability, e.g. (r,s) and (r,-s)are both valid signatures, lead to blockchain network split'''
def Malleability(mes):
    [r,s] = Sig(sk,mes,k)
    print('(4)Malleability, e.g. (r,s) and (r,-s)are both valid signatures, lead to blockchain network split')
    verify_with_m(mes,r,s,pk)
    verify_with_m(mes,r,(-s)%N,pk)
```
### One can forge signature if the verification does not check m
此处实现，如果验证的过程不需要check明文消息m那么任何一个人都可以伪造签名，这里需要借助在准备阶段实现的verify_without_m函数进行验证。具体实现如下：
```python
'''One can forge signature if the verification does not check m'''
def forge():
    print("(6)One can forge signature if the verification does not check m")
    k1 = secrets.randbelow(N)
    k2 = secrets.randbelow(N)
    g1 = mathfunc.ECC_mul(k1,G)
    g2 = mathfunc.ECC_mul(k2,pk)
    [r1,s1] = mathfunc.ECC_add(g1,g2)
    r_k1 = r1*k1
    k2_ = mathfunc.cal_inverse(k2,N)
    e1 = (r_k1*k2_) % N
    s1 = (r1*k2_) % N
    if (verify_without_m(e1, r1, s1, pk)):
        print('forge伪造成功')
```
### Same d and k with ECDSA, leads to leaking of d'
这里实现若另一个签名算法与ECDSA使用相同的k与A，那么依然会导致私钥d的泄露。这里具体的签名算法选择的是Schnorr签名算法。因此在此处首先实现Schnorr签名算法如下,其传入参数为私钥sk以及明文消息mes：
```python
'''Same d and k with ECDSA, leads to leaking of d'''
def Schnorr(sk, mes):
    g1 = mathfunc.ECC_mul(k,G)
    e = int(sha256((str(g1[0]) + mes).encode('utf-8')).hexdigest(), 16)
    s= (k + e * sk) % N
    return g1,e,s
```
其次再实现泄露d的过程，此处传入的参数仍是私钥sk以及明文消息mes，这里尽管使用两种签名算法但他们使用的d以及k均是相同的，计算过程如下所示：
```python
def same_d_k(sk, mes):
    print("(7)Same d and k with ECDSA, leads to leaking of d")
    g1 = mathfunc.ECC_mul(k,G)
    e = int(sha256((str(g1[0]) + str(mes)).encode('utf-8')).hexdigest(), 16)
    s= (k + e * sk) % N
    e1 = int(sha256(mes.encode('utf-8')).hexdigest(), 16)
    [r1,s1] = Sig(sk,mes,k)

    s1_ = e1 + r1*sk
    s1__ = mathfunc.cal_inverse((s - e * sk) % N, N)
    s1 = (s1_*s1__) % N

    d_ = s1*s - e1
    d__ = mathfunc.cal_inverse(s1*e+r1,N)
    d = (d_*d__) % N
    print('签名时使用的私钥d:', sk)
    print('与ECDSA使用相同的d、k从而计算出的私钥d:',d)
    print('使用相同d、k计算出的结果是否相等',sk==d)
```
### 主函数展示
在实现上述所需要使用的函数后，在主函数中依次调用即可，具体代码实现如下：
```python
if __name__=='__main__':
    text1 = "1234567890"
    text2 = "0987654321"
    '''先进行一次ecdsa签名'''
    k = secrets.randbelow(P)
    sign_ecdsa = Sig(sk, text1, k)
    [r, s] = sign_ecdsa
    '''Leaking k leads to leaking of d'''
    Leaking_k(text1,r,s)
    print("--------------------")

    '''Reusing k leads to leaking of d'''
    sk1, pk1 = mathfunc.generate_key()
    Reuseing_k(sk1, text1, text2)
    print("--------------------")

    '''Two users, using k leads to leaking of d, that is they can deduce each other’s d'''
    sk11, pk11 = mathfunc.generate_key()
    sk22, pk22 = mathfunc.generate_key()
    reusing_k_by_2(sk11, sk22, text1, text2)
    print("--------------------")

    '''Malleability, e.g. (r,s) and (r,-s)are both valid signatures, lead to blockchain network split'''
    Malleability(text1)
    print("--------------------")

    '''One can forge signature if the verification does not check m'''
    forge()
    print("--------------------")

    '''Same d and k with ECDSA, leads to leaking of d'''
    same_d_k(sk, text1)
```
## 打印结果展示
![图片](https://user-images.githubusercontent.com/105708747/181269210-ea9e55cf-67be-464c-af37-28493259b5da.png)
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
