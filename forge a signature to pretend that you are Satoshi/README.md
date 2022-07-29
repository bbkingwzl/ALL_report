# forgeasignature-to-pretend-that-you-are-Satoshi
forge a signature to pretend that you are Satoshi，本次实验为笔者独自完成。引用部分在文中有所展示。
## 运行解释以及注意事项
在导入所给py文件mathfunc后，在运行时直接下载py文件运行main.py文件即可。
## main函数介绍
因为此处与SM2实验中的pitfalls_verify任务中的第六条相同，此处直接对pitfalls_verify中的相关函数进行引用。主函数实现如下：
```python
import pitfalls_verify

if __name__=='__main__':
    pitfalls_verify.forge()
```
## forge函数具体介绍
在实现forge函数前，需要先实现一个verify_without_m函数，即不check m的情况下进行验证。其输入为一个哈希值e，签名结果r、s，以及公钥pk。此过程需要利用e、r、s生成两个坐标g1、g2并相加得到一个新点g，随后检查其横坐标x是否与r相同。
```python
'''verification does not check m'''
def verify_without_m(e,r,s,pk):
    s_ = mathfunc.cal_inverse(s, N) % N
    es_ = e*s_ % N
    rs_ = r*s_ % N
    g1 = mathfunc.ECC_mul(es_,G)
    g2 = mathfunc.ECC_mul(rs_,pk)
    g = mathfunc.ECC_add(g1, g2)
    [x, y] = g
    if(x == r):
        print("pass verify")
        return True
    else:
        print("unpass verify")
        return False
```
最后实现如果验证的过程不需要check明文消息m那么任何一个人都可以伪造签名，这里需要借助在准备阶段实现的verify_without_m函数进行验证。此过程需要首先生成两个随机数k1、k2并利用这两个随机数生成两个随机坐标g1、g2类似上述verify的过程将其相加得到新的坐标，进行运算后传入verify_without_m函数进行验证。
```python
'''One can forge signature if the verification does not check m'''
def forge():
    print("(6)One can forge signature if the verification does not check m")
    k1 = secrets.randbelow(N)
    k2 = secrets.randbelow(N)
    g1 = mathfunc.ECC_mul(k1,G)
    g2 = mathfunc.ECC_mul(k2,pk)
    [r1,s1] = mathfunc.ECC_add(g1,g2)
    r_k1 = r1*k1
    k2_ = mathfunc.cal_inverse(k2,N)
    e1 = (r_k1*k2_) % N
    s1 = (r1*k2_) % N
    if (verify_without_m(e1, r1, s1, pk)):
        print('forge伪造成功')
```
## 打印结果展示
![图片](https://user-images.githubusercontent.com/105708747/181743044-a30b52c7-29ed-4466-9378-0b21c075ac3a.png)
