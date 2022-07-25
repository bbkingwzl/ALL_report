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

'''PKEnc,SM2算法加密会话密钥K'''
def PKEnc(M, K):
    C = sm2.CryptSM2(public_key=K[1], private_key=K[0]).encrypt(M)
    return C

'''PKDec,SM2算法解密得到会话密钥K'''
def PKDec(C, K):
    M = sm2.CryptSM2(public_key=K[1], private_key=K[0]).decrypt(C)
    return M

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


if __name__ == '__main__':
    M = "this report author is bbkingwzl！"
    print("发送方所发送的M：", M)
    K = hex(random.randint(2 ** 127, 2 ** 128))[2:]
    print("会话密钥K：", K)
    M1, K1 = Encrypt(M, K)
    Decrypt(M1, K1)
