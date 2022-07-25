# sm2_rfc6979
impl sm2 with rfc6979
## RFC6979生成随机数k原理
首先分析RFC6979生成随机数k的原理，我们定义:
```python
    HMAC_K(V)
```
使用密钥(key)K对数据V进行HMAC算法。
给定输入消息m，应用以下过程：

1.通过哈希函数H处理m，产生：
```python
h1 = H（m）
```
2. V（以比特）的长度等于8 * ceil（hlen / 8）。例如，如果H是SHA-256，则V被设置为值为1的32个八位字节的序列。
```python
V = 0x01 0x01 0x01 ... 0x01
```
3.K的长度（以比特）等于8 * ceil（hlen / 8）。
```python
K = 0x00 0x00 0x00 ... 0x00
```
4.‘||’表示连接。x是私钥。
```python
K = HMAC_K（V || 0x00 || int2octets（x）|| bits2octets（h1））
```
5. 对V进行HMAC处理
```python
V = HMAC_K（V）
```
6.按照规则已经V对K进行处理
```python
K = HMAC_K（V || 0x01 || int2octets（x）|| bits2octets（h1））
```
7.再对V进行一次处理
```python
V = HMAC_K（V）
```
8执行以下流程，直到找到适当的值k：  
8.1将T设置为空序列。 T的长度（以比特为单位）表示为tlen, 因此tlen = 0。
```python
V = HMAC_K（V）
T = T || V
k = bits2int（T）
```
8.2如果k的值在[1，q-1]范围内，那么k的生成就完了。否则，计算：
```python
K = HMAC_K（V || 0x00）
V = HMAC_K（V）
```
并循环（尝试生成一个新的T，等等）。
## 按照RFC6979生成随机数k函数具体实现
bin_sha256()返回输入数据的hash256的结果，不过是python的byte格式的（也就是字符串在计算机的真正样子）。比如这里的
```python
i = 1
result_k = deterministic_generate_k(bin_sha256(str(i)), encode(i, 256, 32))
print result_k
```
最终定义函数deterministic_generate_k生成随机数k
```python
def deterministic_generate_k(msghash, priv):
    v = b'\x01' * 32
    k = b'\x00' * 32

    priv = encode_privkey(priv, 'bin')

    msghash = encode(hash_to_int(msghash), 256, 32)

    k = hmac.new(k, v+b'\x00'+priv+msghash, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    k = hmac.new(k, v+b'\x01'+priv+msghash, hashlib.sha256).digest()
    v = hmac.new(k, v, hashlib.sha256).digest()
    return decode(hmac.new(k, v, hashlib.sha256).digest(), 256)
```
## 根据RFC6979实现SM2
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

'''设置函数参数a=0，b=7，则函数方程为y^2=x^3+7'''
A = 0
B = 7

'''生成私钥、公钥'''
private_key, public_key = mathfunc.generate_key()
```
根据ZA的定义进行precomputer，需要将个人的ID，椭圆曲线参数a、b,基本点的坐标x、y以及公钥pk1、pk2进行级联。
![图片](https://user-images.githubusercontent.com/105708747/180604348-815b5023-b0bb-41ea-9dfb-52cd82471c8b.png)
```python
'''计算ZA'''
def cal_ZA(ID, A1, B1, X1, Y1, pk1, pk2):
    #获取bit位数
    ENTLA=str(len(ID.encode()) << 3)
    #将所有输入混合进行拼接后利用sha256进行哈希
    mix_mes = ENTLA + ID + str(A1) + str(B1) + str(X1) + str(Y1) + str(pk1) + str(pk2)
    hash = int(sha256(mix_mes.encode('utf-8')).hexdigest(),16)
    return hash
```
利用生成的私钥对信息mes进行签名，这里使用的hash函数为sha256.在完成哈希后，需要生成一个随机数k，在生成随机数时，根据RFC6979中生成一个随机数k。而后利用该随机数k与基本点相乘得到一个随机点。其原理以及代码实现如下：
![图片](https://user-images.githubusercontent.com/105708747/180604467-0d1818c9-c1f3-44a3-9eac-87bca46acfae.png)
```python
'''签名'''
def Sig(pk, mes, ZA):
    hash1 = sha256(str(ZA+mes).encode('utf-8')).hexdigest()
    hash2 = int(hash1,16)
    # 生成随机数k，利用k与基本点相乘得到一个随机的点G
    k = bitcoin.main.deterministic_generate_k(hash1,private_key)
    #k = 1
    G = mathfunc.ECC_mul(k, basic_point)

    sign = []
    sign.append(( hash2+G[0] ) % P2)
    sign.append((mathfunc.cal_inverse(1 + pk, P2) * (k - sign[0] * pk)) % P2)  #用私钥进行签名
    return sign

mes = "1234567890"
ID='bbkingwzl'
ZA=str(cal_ZA(ID, A, B, X, Y, public_key[0], public_key[1]))
sign = Sig(private_key, mes, ZA)
print("签名: ",sign)
```
最后，进行验证工作验证r与R是否相等。在check函数中，仍需先对ZA进行哈希，随后根据下图所示原理进行实现。
![图片](https://user-images.githubusercontent.com/105708747/180604478-8540acd8-3a6b-4451-85e6-b39f94d5dfaf.png)
```python
'''验证'''
def check(public_key, ID, mes, sign):
    ZA=str(cal_ZA(ID, A, B, X, Y, public_key[0], public_key[1]))
    hash = int(sha256(str(ZA+mes).encode('utf-8')).hexdigest(),16)

    mul1=mathfunc.ECC_mul(sign[1], basic_point)
    mul2=mathfunc.ECC_mul((sign[0]+sign[1]) % P2, public_key)
    add1=mathfunc.ECC_add(mul1, mul2)

    sk1= (hash+add1[0]) % P2
    print('私钥:',sign[0])
    print('计算得出的私钥',sk1)

    return sk1==sign[0]

if(check(public_key, ID, mes, sign)):
    print('验证通过')
```
对最终结果进行打印，最终结果如下： 
![图片](https://user-images.githubusercontent.com/105708747/180604507-7a31835a-c403-4764-afcd-a05456b4776f.png)
## mathfunc中函数介绍
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
再构造SM2所需使用的数学函数，分别是利用扩展欧几里得算法求逆以及Tonelli-Shanks求解二次剩余
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

