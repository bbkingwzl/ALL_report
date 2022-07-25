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

print('真实公钥：', public_key)
print("利用私钥得到的签名: ", sign)
print('根据签名和消息，推测出公钥：')
print('可能公钥1：', key1_possible)
print('可能公钥2：', key2_possible)
