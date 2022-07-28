# PoC_password_check_up
PoC impl of the scheme, or do implement analysis by Google,本次实验为笔者独自完成。引用部分在文中有所展示。
## 运行解释以及注意事项
在导入所提供的mathfunc文件后，导入gmssl，在运行时直接下载py文件运行PoC.py即可。
## PoC流程具体实现
### 准备阶段
导入所需库（mathfunc为笔者所编写），gmssl库中导入sm3后。生成模数n，以及客户端与服务端的私钥a、b和用户名以及密码。这里为了便于操作将username与password设置为相同的字符串。
```python
from gmssl import sm3,func
import mathfunc
import secrets
n = 65535 #模数n
a = secrets.randbelow(n)#Client sk：a
b = secrets.randbelow(n)#Server sk：a
username = 'bbkingwzl' #Client username
password = 'bbkingwzl' #Client password
```
### (1)Process data info and (3)Find the data set 
此过程在服务端进行实现，其具体操作如下所示：  
![图片](https://user-images.githubusercontent.com/105708747/181577863-3fc6b58c-fb0c-4d12-9f41-96fc52c72283.png)   
传入参数k，v由客户端进行输入，b为服务端持有的私钥。
```python
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
```
### (2)User input name and password:(u,p)
此过程在客户端进行实现，参数u，p为用户名以及password，a为客户端持有的私钥，其具体操作如下所示：
![图片](https://user-images.githubusercontent.com/105708747/181583593-f54569b1-7684-403a-a94e-feec698e4e45.png)
```python
def Client_input_up(u, p, a):
    up = bytes(u + p, encoding='utf-8')
    h = sm3.sm3_hash(func.bytes_to_list(up))
    k = h[:2]
    v = (pow(int(h, 16), a)) % n
    return k, v
```
### (4)Username and password detection
此过程在客户端进行实现，参数h_ab以及set_S为服务端传送的计算结果，a为客户端持有的私钥a，其具体操作如下所示：
![图片](https://user-images.githubusercontent.com/105708747/181588498-b268c279-1845-4933-81ea-609cec9d67cd.png)
```python
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
```
### 主函数代码展示
在主函数逐次调用上述实现函数即可，代码如下：
```python
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

```
### 打印结果展示：
![图片](https://user-images.githubusercontent.com/105708747/181588785-cd68a836-a39d-4ec8-8676-0131964e9d88.png)
