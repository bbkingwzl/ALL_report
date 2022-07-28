from gmssl import sm3,func
import mathfunc
import secrets

'''(1)Process data info and (3)Find the data set'''
def Server(k, v, b):
    '''Process data info'''
    data_records = []
    for u in range(0, pow(2, 16)):
        p = u
        up = bytes(str(u)+str(p),encoding='utf-8')
        h = sm3.sm3_hash(func.bytes_to_list(up))
        data_records.append(h)
    set_S = []
    for hi in data_records:
        if hi[:2] == k:
            set_S.append((pow(int(hi, 16), b)) % n)
    '''Find the data set'''
    h_ab = (pow(v, b)) % n
    return h_ab, set_S

'''(2)User input name and password:(u,p)'''
def Client_input_up(u, p, a):
    up = bytes(u + p, encoding='utf-8')
    h = sm3.sm3_hash(func.bytes_to_list(up))
    k = h[:2]
    v = (pow(int(h, 16), a)) % n
    return k, v

'''(4)Username and password detection'''
def Client_detection(h_ab, set_S, a):
    a_ = mathfunc.cal_inverse(a,n-1)
    h_b = (pow(h_ab, a_)) % n
    flag = False
    for s in set_S:
        if s == h_b:
            flag = True
    if (not flag):
        print('usename', username, 'safe')
    else:
        print('username', username, 'unsafe')


if __name__ == '__main__':
    n = 65535 #模数n
    a = secrets.randbelow(n)#Client sk：a
    b = secrets.randbelow(n)#Server sk：a
    username = 'bbkingwzl' #Client username
    password = 'bbkingwzl' #Client password
    '''生成(k,v)发送至Server'''
    k, v = Client_input_up(username, password, a)
    '''客户端生成h_ab以及集合S'''
    h_ab, set_S = Server(k, v, b)
    '''检查h_b是否在集合S中'''
    Client_detection(h_ab, set_S, a)













