iv='7380166f4914b2b9172442d7da8a0600a96f30bc163138aae38dee4db0fb0e4e'

def t(j):
    if j<16:
        return 0x79cc4519
    return 0x7a879d8a

def csl(x,k):#cycle_shift_left
    x='{:032b}'.format(x)
    k=k%32
    x=x[k:]+x[:k]
    return int(x,2)

#bool function
def ff(x,y,z,j):
    if j<16:
        return x^y^z
    return (x&y)|(y&z)|(z&x)
def gg(x,y,z,j):
    if j<16:
        return x^y^z
    return (x&y)|(~x&z)

#displace function
def p0(x):
    return x^csl(x, 9)^csl(x, 17)
def p1(x):
    return x^csl(x, 15)^csl(x, 23)

#plaintext:m(length<2^64bit)
def fill(m):
    l=len(m)*4
    m=m+'8'
    k=112-(len(m)%128)
    m=m+'0'*k+'{:016x}'.format(l)
    return m

def grouping(m):
    n=len(m)//128
    b=[]
    for i in range(n):
        b.append(m[i*128:(i+1)*128])
    return b

def extend(bi):
    w=[]
    for i in range(16):
        w.append(int(bi[i*8:(i+1)*8],16))
    for j in range(16,68):
        w.append(p1(w[j-16]^w[j-9]^csl(w[j-3], 15))^csl(w[j-13], 7)^w[j-6])
    for j in range(68,132):
        w.append(w[j-68]^w[j-64])
    return w

def cf(vi,bi):
    w=extend(bi)
    a,b,c,d,e,f,g,h=int(vi[0:8],16),int(vi[8:16],16),int(vi[16:24],16),int(vi[24:32],16),int(vi[32:40],16),int(vi[40:48],16),int(vi[48:56],16),int(vi[56:64],16)
    for j in range(64):
        ss1=csl((csl(a,12)+e+csl(t(j),j))%pow(2,32),7)
        ss2=ss1^csl(a,12)
        tt1=(ff(a,b,c,j)+d+ss2+w[j+68])%pow(2,32)
        tt2=(gg(e,f,g,j)+h+ss1+w[j])%pow(2,32)
        d=c
        c=csl(b,9)
        b=a
        a=tt1
        h=g
        g=csl(f,19)
        f=e
        e=p0(tt2)
    abcdefgh=int('{:08x}'.format(a)+'{:08x}'.format(b)+'{:08x}'.format(c)+'{:08x}'.format(d)+'{:08x}'.format(e)+'{:08x}'.format(f)+'{:08x}'.format(g)+'{:08x}'.format(h),16)
    return '{:064x}'.format(abcdefgh^int(vi,16))

def iteration(b):
    n=len(b)
    v=iv
    for i in range(n):
        v=cf(v,b[i])
    return v

def sm3hash(m):#m为16进制串
    m=fill(m)
    b=grouping(m)
    return iteration(b)
