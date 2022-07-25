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
print('公钥：',public_key)

'''计算ZA'''
def cal_ZA(ID, A1, B1, X1, Y1, pk1, pk2):
    #获取bit位数
    ENTLA=str(len(ID.encode()) << 3)
    #将所有输入混合进行拼接后利用sha256进行哈希
    mix_mes = ENTLA + ID + str(A1) + str(B1) + str(X1) + str(Y1) + str(pk1) + str(pk2)
    hash = int(sha256(mix_mes.encode('utf-8')).hexdigest(),16)
    return hash


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

