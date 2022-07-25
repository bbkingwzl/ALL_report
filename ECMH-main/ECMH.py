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