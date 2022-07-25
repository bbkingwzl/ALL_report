# ECMH
Implement the above ECMH scheme  本次实验为笔者独自完成。引用部分在文中有所展示。
## 运行解释以及注意事项
除mathfunc导入外，还需要导入gmssl库，在运行前需要先pip install gmssl
在运行时直接下载py文件运行ECMH即可。
另外是本次代码上传时间为多天前，但由于需要重新上传至总库因此时间改变，具体实现时间为2022-7-24：  
![图片](https://user-images.githubusercontent.com/105708747/180754733-2bd9dbcf-2748-42d7-b563-9f012aaa4fd0.png)

## ECMH实现介绍
导入所需库后（mathfunc为笔者所编写的py文件），设置有限域的阶以及椭圆曲线的阶以及基本点,而后设置椭圆曲线相关参数a、b。
```python
from gmssl import sm3, func
import mathfunc

'''设置椭圆曲线参数'''
a = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93
'''设置有限域的阶以及椭圆曲线的阶'''
P1 = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
P2 = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
X = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Y = 32670510020758816978083085130507043184471273380659243275938904335757337482424
basic_point = (X, Y)
```
构造集合的哈希，首先初始化一个无穷远点为0.随后遍历集合中的元素，借助sm3哈希产生一个椭圆曲线上的点的横坐标X，随后将X代入椭圆曲线方程，根据Tonelli_Shanks求出其逆元，随后与初始设置的无穷远点相加。在完成遍历后返回该集合的哈希值。
```python
'''集合的哈希'''
def MultiSetHash(set_2_hash):
    set_hash = 0 #初始化为无穷远点
    for i in set_2_hash: #遍历集合中元素
        point = [] #借助sm3产生一个椭圆曲线中的点
        point.append(int(sm3.sm3_hash(func.bytes_to_list(i)), 16))#使用sm3对集合元素进行哈希
        hash1 = (point[0] ** 2 + a * point[0] + b)% P1#代入椭圆曲线求出纵坐标
        point.append(mathfunc.Tonelli_Shanks(hash1, P1))
        set_hash = mathfunc.ECC_add(set_hash, point)#集合的哈希
    return set_hash
```
在主函数中生成公私钥对sk、pk并进行打印。而后设置三个集合分别为set1 = (b'bbkingwzl',)、set2 = (b'bbkingwzl', b'lzwgnikbb')、set3 = (b'lzwgnikbb',)课件set1Uset3 = set2.随后对他们求集合的哈希并进行打印输出。
```python
if __name__ == '__main__':
    [sk, pk] = mathfunc.generate_key()
    print('公私钥对为：',[sk,pk])
    set1 = (b'bbkingwzl',)
    set2 = (b'bbkingwzl', b'lzwgnikbb')
    set3 = (b'lzwgnikbb',)
    set_hash1 = MultiSetHash(set1)
    set_hash2 = MultiSetHash(set2)
    set_hash3 = MultiSetHash(set3)
    print("hash({b'bbkingwzl'}) = ", set_hash1)
    print("hash({b'lzwgnikbb'}) = ", set_hash3)
    print("hash({b'bbkingwzl', b'lzwgnikbb'}) = ", set_hash2)
```
## 打印结果展示
打印结果如下所示：
![图片](https://user-images.githubusercontent.com/105708747/180641605-fbe4e82e-9ffe-4615-836a-8774f839c06d.png)
## mathfunc中的函数介绍
下面介绍mathfunc.py中的函数。首先设置有限域的阶以及椭圆曲线的阶以及基本点，以及椭圆曲线方程的参数
```python
import secrets
'''设置有限域的阶以及椭圆曲线的阶'''
P1 = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFF
P2 = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFF7203DF6B21C6052B53BBF40939D54123
X = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Y = 32670510020758816978083085130507043184471273380659243275938904335757337482424
basic_point = (X, Y)

'''设置椭圆曲线参数'''
a = 0xFFFFFFFEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000FFFFFFFFFFFFFFFC
b = 0x28E9FA9E9D9F5E344D5A9E4BCF6509A7F39789F515AB8F92DDBCBD414D940E93
```
再构造ECMH所需使用的数学函数，分别是利用扩展欧几里得算法求逆以及Tonelli-Shanks求解二次剩余，这里引用https://blog.csdn.net/qq_51999772/article/details/122642868
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

