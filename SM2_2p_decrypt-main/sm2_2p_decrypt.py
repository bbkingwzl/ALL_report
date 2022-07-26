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

'''(1)Generate sub private key d1、d2'''
d1 = secrets.randbelow(P2-1)
d2 = secrets.randbelow(P2-1)
d1d2_ = mathfunc.cal_inverse(d1 * d2, P1)
P = mathfunc.ECC_mul(d1d2_ - 1, G)
print('Public key P:',P)

def KDF(z, klen):
    ct=1
    k=''
    for _ in range(math.ceil(klen/256)):
        k=k+sm3hash(hex(int(z+'{:032b}'.format(ct),2))[2:])
        ct=ct+1
    k='0'*((256-(len(bin(int(k,16))[2:])%256))%256)+bin(int(k,16))[2:]
    return k[:klen]

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

'''(3) compute T2'''
d2_ = mathfunc.cal_inverse(d2,P1)
T2 = mathfunc.ECC_mul(d2_,T1)
print("计算得到的T2：",T2)

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