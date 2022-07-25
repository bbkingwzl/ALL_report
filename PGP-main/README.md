# PGP
Project: Implement a PGP scheme with SM2，本次实验为笔者独自完成。引用部分在文中有所展示。
## 代码说明以及注意事项
除mathfunc导入外，还需要导入crypto以及gmssl库，在运行前需要先pip install crypto以及pip install gmssl。若在install crypto后仍报错，则先将python的lib文件夹中的Crypto改为小写crypto之后再pip install crypto
在运行时直接下载py文件运行main即可。
另外是本次代码上传时间为多天前，但由于需要重新上传至总库因此时间改变，具体实现时间为2022-7-24： 
![图片](https://user-images.githubusercontent.com/105708747/180754167-811c42ef-2854-4f2e-98d4-f094419cc734.png)

## PGP实现过程
导入所需库后（mathfunc为笔者所编写的py文件），设置有限域的阶以及椭圆曲线的阶以及基本点,再设置椭圆曲线参数，并利用mathfunc中的生成密钥函数进行密钥的生成工作。此时生成的公私钥对为SM2加解密所需使用的sk、pk，即在PKEnc和PKDec中所需使用的密钥。
```python
import random
from Crypto.Cipher import AES
from gmssl import sm2
import mathfunc

'''设置有限域的阶以及椭圆曲线的阶'''
P1 = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
P2 = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
X = 0x32C4AE2C1F1981195F9904466A39C9948FE30BBFF2660BE1715A4589334C74C7
Y = 0xBC3736A2F4F6779C59BDCEE36B692153D0A9877CC62A474002DF32E52139F0A0
basic_point = (X, Y)

'''设置椭圆曲线参数'''
a = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93

[sk, pk] = mathfunc.generate_key()
sk_2_Enc_Dec = hex(sk)[2:]
pk_2_Enc_Dec = hex(pk[0])[2:] + hex(pk[1])[2:]
K_2_SM2 = [sk_2_Enc_Dec, pk_2_Enc_Dec]
```
定义PKEnc以及PKDec函数，其作用分别为使用SM2算法加解密会话密钥K，此处直接使用gmssl库中的sm2库。
```python
'''PKEnc,SM2算法加密会话密钥K'''
def PKEnc(M, K):
    C = sm2.CryptSM2(public_key=K[1], private_key=K[0]).encrypt(M)
    return C

'''PKDec,SM2算法解密得到会话密钥K'''
def PKDec(C, K):
    M = sm2.CryptSM2(public_key=K[1], private_key=K[0]).decrypt(C)
    return M
```
即下图所示两函数。  
![图片](https://user-images.githubusercontent.com/105708747/180671812-8e50c761-6cd9-492d-a3ee-eb100099e71d.png)
![图片](https://user-images.githubusercontent.com/105708747/180671824-52e31171-6823-43fd-bcfb-b7fb5c449913.png)  
下面实现Encrypt功能，其分为SymEnc以及PKEnc两部分，其中PKEnc已在前面进行实现。主要实现SymEnc功能，其利用对称加密算法AES加密发送方所需要发送的消息mes（一般来说使用对称加密算法加密消息，使用公钥密码算法加密密钥）。此处AES使用OFB模式，这里还需要使用PKEnc函数对随机产生的会话密钥K进行加密，总体代码如下：
```python
'''Encrypt,PGP系统所使用的加密，其中包括SymEmc加密消息使用对称密码AES，以及加密K所使用的PKEnc，使用SM2算法'''
def Encrypt(M, K):
    #PKEnc,SM2算法加密会话密钥K
    K_2_PKEnc = K.encode('utf-8')
    pkenc = PKEnc(K_2_PKEnc, K_2_SM2)
    print("PKEnc result：", pkenc)

    iv = b'1234567887654321'
    mode = AES.MODE_OFB
    SymEnc = AES.new(K.encode('utf-8'), mode, iv)
    block = len(M)
    if block % 16 != 0:
        remain = 16 - (block % 16)
    else:
        remain = 0
    M = M + ('\0' * remain)
    C = SymEnc.encrypt(M.encode('utf-8'))
    print("SymEnc result：", C)

    return C, pkenc
```
其实现的总体示意图如下：  
![图片](https://user-images.githubusercontent.com/105708747/180672032-476d6ebd-60a6-451d-b576-66fee5e3449c.png)  
下面实现Decrypt功能，其分为SymDec以及PKDec两部分，其中PKDec已在前面进行实现。主要实现SymDec功能，其利用对称加密算法AES解密发送方发送的消息cipher。在接收方接收到密文后，首先需要对发送方加密的AES使用的会话密钥K进行解密，此处使用的解密函数即为PKDec，而后再利用K、AES对cipher进行解密，代码如下：
```python
'''Decrypt,PGP系统所使用的解密，其中包括SymDec解密消息使用对称密码AES，以及解密K所使用的PKDec，使用SM2算法'''
def Decrypt(C, pkenc):
    #PKDec,SM2算法解密得到会话密钥K
    pkdec = PKDec(pkenc, K_2_SM2)
    print("PKDec result：", pkdec.decode('utf-8'))

    iv = b'1234567887654321'
    mode = AES.MODE_OFB
    SymDec = AES.new(pkdec, mode, iv)
    M = SymDec.decrypt(C)

    print("接收方解密得到的M：", M.decode('utf-8'))
```
其实现的总体示意图如下：  
![图片](https://user-images.githubusercontent.com/105708747/180672206-6618ee65-9ac7-472a-943b-83ee6fa55562.png)  
最终在主函数中对整个过程进行调用，注意K生成时的范围为2^127,2^128.
```python
if __name__ == '__main__':
    M = "this report author is bbkingwzl！"
    print("发送方所发送的M：", M)
    K = hex(random.randint(2 ** 127, 2 ** 128))[2:]
    print("会话密钥K：", K)
    M1, K1 = Encrypt(M, K)
    Decrypt(M1, K1)
```
## 打印结果展示
打印结果如下：  
![图片](https://user-images.githubusercontent.com/105708747/180672266-b273d5fc-06c3-48d4-9c0f-622a24d0579a.png)
## mathfunc中的函数介绍
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

