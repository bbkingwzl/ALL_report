# ALL_report
总代码仓库，总计完成20个project
# 个人信息
本次项目均为个人实现，无小组成员。本仓库中提交时间较集中的原因是开始并没有push进入一个代码仓库中，因此在每个小project中均标明具体的提交时间。
```
姓名：魏照林
学号：202000460083
账号：bbkingwzl
```
# 仓库介绍以及项目清单
为了便于下载，笔者将所有的project均放入一个仓库中。本次总结完成20个项目，其中18个项目为课内所布置任务(仅有两个课内任务没有完成)，两个项目为笔者自己添加的内容，下面将进行项目的罗列。  
已完成项目：
```
SM3:

1.Project: implement the naïve birthday attack of reduced SM3
2.Project: implement the Rho method of reduced SM3
3.Project: implement length extension attack for SM3, SHA256, etc.
4.Project: do your best to optimize SM3 implementation (software)
5.Project: Impl Merkle Tree following RFC6962
```
```
SM2:

6.*Project: report on the application of this deduce technique in Ethereum with ECDSA
7.*Project: impl sm2 with RFC6979
8.*Project: verify the above pitfalls with proof-of-concept code
9.*Project: Implement the above ECMH scheme
10.*Project: Implement a PGP scheme with SM2
11.*Project: implement sm2 2P sign with real network communication
12.*Project: PoC impl of the scheme, or do implement analysis by Google
13.*Project: implement sm2 2P decrypt with real network communication
```
```
Bitcoin-public:

14.*Project: send a tx on Bitcoin testnet, and parse the tx data down to every bit, better write script yourself
15.*Project: forge a signature to pretend that you are Satoshi
```
```
Eth-public:

16.Project: research report on MPT
```
```
Real world cryptanalyses:

17.Project: Find a key with hash value “sdu_cst_20220610” under a message composed of your name followed by your student ID. For example, “San Zhan 202000460001”.
```
```
Real world zk:

18.Project Idea 1. Write a circuit to prove that your CET6 grade is larger than 425. a. Your grade info is like (cn_id, grade, year, sig_by_moe). These grades are published as commitments onchain by MoE. b. When you got an interview from an employer, you can prove to them that you have passed the exam without letting them know the exact grade. 2. The commitment scheme used by MoE is SHA256-based. a. commit = SHA256(cn_id, grade, year, sig_by_moe, r)
```
```
Extra project:

19.SM4_Mode_ECB_CBC
20.SM4_optimization
```
未完成项目：
```
1.SM3 Project: Try to Implement this scheme
2.Real world cryptanalyses Project: Find a 64-byte message under some  fulfilling that their hash value is symmetrical
```
# 项目简介及链接
## 1.SM3_Birthday_Attack
本实验实现SM3生日攻击，由于算力有限，仅截取hash值的前32位作为结果。  
https://github.com/bbkingwzl/ALL_report/tree/main/SM3_Birthday_Attack-main
## 2.SM3_rho_method
本实验实现SM3rho method attack，由于算力有限，仅截取hash值的前32位作为结果。  
https://github.com/bbkingwzl/ALL_report/tree/main/SM3_rho_method-main
## 3.SM3_length_extension_attack
本实验依照PPT流程实现SM3的长度扩展攻击。  
https://github.com/bbkingwzl/ALL_report/tree/main/SM3_length_extension_attack-main
## 4.SM3_optimization
本实验利用SIMD指令集对SM3进行优化，其中包含运行时间测试。  
https://github.com/bbkingwzl/ALL_report/tree/main/SM3_optimization-main
## 5.merkle_tree
本实验实现了简单的Merkle tree以及其存在性证明。  
https://github.com/bbkingwzl/ALL_report/tree/main/merkle_tree-main
## 6.ECDSA_deduce
本实验不局限于以report的形式学习ECDSA，并以代码的形式具体实现了ECDSA_deduce  
https://github.com/bbkingwzl/ALL_report/tree/main/ECDSA_deduce-main
## 7.sm2_rfc6979
本实验按照rfc6979产生随机数k并实现了sm2算法。  
https://github.com/bbkingwzl/ALL_report/tree/main/sm2_rfc6979-main
## 8.pitfalls_verify
本实验验证了PPT所提及的六种情况所能发生的私钥泄露问题。  
https://github.com/bbkingwzl/ALL_report/tree/main/pitfalls_verify
## 9.ECMH
本实验实现了将集合哈希到椭圆曲线点的ECMH方案。  
https://github.com/bbkingwzl/ALL_report/tree/main/ECMH-main
## 10.PGP
本实验依照PPT流程实现了PGP方案。  
https://github.com/bbkingwzl/ALL_report/tree/main/PGP-main
## 11.sm2_2p_sign
本实验依照PPT流程实现了两方签名方案。  
https://github.com/bbkingwzl/ALL_report/tree/main/sm2_2P_sign-main
## 12.PoC_password_check
本实验依照PPT流程实现了PoC password check方案。  
https://github.com/bbkingwzl/ALL_report/tree/main/PoC_password_check_up-main
## 13.SM2_2p_decrypt
本实验依照PPT流程实现了两方解密方案。  
https://github.com/bbkingwzl/ALL_report/tree/main/SM2_2p_decrypt-main
## 14.parse_the_tx_data
本实验由于测试币并没有申请成功，因此选取了一笔交易以进行分析。  
https://github.com/bbkingwzl/ALL_report/tree/main/parse_the_tx_data
## 15.forge a signature to pretent that you are Satoshi
本实验依据前述的pitfalls_verify进行了伪造。  
https://github.com/bbkingwzl/ALL_report/tree/main/forge%20a%20signature%20to%20pretend%20that%20you%20are%20Satoshi
## 16.report_on_MPT
本实验对于以太坊MPT（Merkle Patricia Tree）进行了学习，以读书笔记的形式进行呈现。  
https://github.com/bbkingwzl/ALL_report/tree/main/report_on_MPT
## 17.find-key
本实验实现了在固定哈希值以及message的情况下寻找key。  
https://github.com/bbkingwzl/ALL_report/tree/main/find-key-main
## 18.circuit-to-prove-CET6-grade
本实验在参照基于circom、snarkjs实现零知识证明不透漏具体地理位置的区域监控的示例的基础上，实现了CET6分数大于425的证明.  
https://github.com/bbkingwzl/ALL_report/tree/main/circuit-to-prove-CET6-grade
## 19.SM4
本实验实现了SM4的ECB以及CBC方案并对比了效率。  
https://github.com/bbkingwzl/ALL_report/tree/main/SM4
## 20.SM4_optimization
本实验为课内实验内容，实现了SM4的查表优化、SIMD指令集加速以及多线程优化。  
https://github.com/bbkingwzl/ALL_report/tree/main/SM4_optimization-main
# 其他事宜
代码说明、运行说明以及运行截图、参考内容等都在各个project中的readme中有所体现，详见其中内容。
