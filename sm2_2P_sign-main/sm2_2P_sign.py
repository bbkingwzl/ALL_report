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

def cal_ZA(ID, a, b, X, Y, sk, pk):

    ENTL=str(len(ID.encode()) << 3)

    joint= ENTL + ID + str(a) + str(b) + str(X) + str(Y) + str(sk) + str(pk)
    joint_bytes=bytes(joint,encoding='utf-8')
    hash= sm3.sm3_hash(func.bytes_to_list(joint_bytes))
    return int(hash, 16)

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
