# parse-the-tx-data
send a tx on Bitcoin testnet, and parse the tx data down to every bit,本次实验为笔者独自完成。引用部分在文中有所展示.
## 运行解释以及注意事项
在向Bitcoin testnet发送测试tx时需要申请测试用的测试币，但由于时间原因在实现本次项目时并未申请成功。在与多位同学讨论后决定选择BlockCypher Testnet Explorer中的一个交易进行分析，（此处借鉴楚良浩同学的意见）。利用网站提供的API，此处我选择的交易为下图所示  
![图片](https://user-images.githubusercontent.com/105708747/181669940-3103ed85-7704-4210-9eb2-e499531e1061.png)
## 交易详情分析
### 总体概括
其次分析本次交易，即分析tx中的内容。从总体来看，本次交易分为一笔输入以及两笔输出。可以看到其中包含本次交易中的哈希值以及版本号等，而地址共有
"mkHS9ne12qx9pS9VojpwU5xtRd4T7X7ZUt","tb1q9z8m6pg9rdvvs5fc7amh7cpx09nx37sqwnvjee","tb1qj45pxpa4p22d4mlejx3jy022hnd43ua6jrjn3m"三个address，这将会在后续的input和output中有所体现。我们能看到交易哈希、版本号、total值即为剩余总值，received代表接收到的日期为7-28 13:28:21，double_spend为false则为解决双花问题。区别于去块头，此处还存在vin_sz以及vout_sz。（值得注意的是，若为第一笔交易则为coinbase交易，即由挖矿产生的比特币奖励。但这里并不是第一笔交易因此不存在这个情况。）下面将会从输入输出角度进行分析。
```
{
  "block_height": -1,
  "block_index": -1,
  "hash": "8eb6e4f7c77ffcfbadac50d0e52156d4e26fa088ac6b584430e11d4e1b0f4f9e",
  "hex": "010000000001018adc854444d7d520be2f7028b45a361d7a44024950884be21964129cb49e46fe0000000000ffffffff028dec96010000000016001495681307b50a94daeff991a3223d4abcdb58f3ba3a650000000000001976a914344a0f48ca150ec2b903817660b9b68b13a6702688ac024730440220698481f25aa5265b59363a2d381f804f76a7d25b42ca4b788d45ad1880e9515d02204f54754e6eaca8cfd961fcba98b0d2f842f01179803b6271dc3f602e7f1a0b8a012102b9af5bd28475739238b9c99b7033547ad1fad2268c85e9675c4df6cafe57a81500000000",
  "addresses": [
    "mkHS9ne12qx9pS9VojpwU5xtRd4T7X7ZUt",
    "tb1q9z8m6pg9rdvvs5fc7amh7cpx09nx37sqwnvjee",
    "tb1qj45pxpa4p22d4mlejx3jy022hnd43ua6jrjn3m"
  ],
  "total": 26694087,
  "fees": 145,
  "size": 225,
  "vsize": 144,
  "preference": "low",
  "relayed_by": "170.75.165.230:18333",
  "received": "2022-07-28T13:28:21.722Z",
  "ver": 1,
  "double_spend": false,
  "vin_sz": 1,
  "vout_sz": 2,
  "confirmations": 0,
  "inputs": [
    {
      "prev_hash": "fe469eb49c126419e24b88504902447a1d365ab428702fbe20d5d7444485dc8a",
      "output_index": 0,
      "output_value": 26694232,
      "sequence": 4294967295,
      "addresses": [
        "tb1q9z8m6pg9rdvvs5fc7amh7cpx09nx37sqwnvjee"
      ],
      "script_type": "pay-to-witness-pubkey-hash",
      "age": 0,
      "witness": [
        "30440220698481f25aa5265b59363a2d381f804f76a7d25b42ca4b788d45ad1880e9515d02204f54754e6eaca8cfd961fcba98b0d2f842f01179803b6271dc3f602e7f1a0b8a01",
        "02b9af5bd28475739238b9c99b7033547ad1fad2268c85e9675c4df6cafe57a815"
      ]
    }
  ],
  "outputs": [
    {
      "value": 26668173,
      "script": "001495681307b50a94daeff991a3223d4abcdb58f3ba",
      "addresses": [
        "tb1qj45pxpa4p22d4mlejx3jy022hnd43ua6jrjn3m"
      ],
      "script_type": "pay-to-witness-pubkey-hash"
    },
    {
      "value": 25914,
      "script": "76a914344a0f48ca150ec2b903817660b9b68b13a6702688ac",
      "addresses": [
        "mkHS9ne12qx9pS9VojpwU5xtRd4T7X7ZUt"
      ],
      "script_type": "pay-to-pubkey-hash"
    }
  ]
}
```
### input分析
通过分析input包含信息可以发现，其包括前一区块的哈希值（prev_hash）以及输出的值(output_value)系列、地址等等。从script_type可以看出这不是一笔标准的 Pay-to-Public-Key-Hash (P2PKH) 交易类型，而使用隔离见证策略存在一个witness的Pay-to-Witness-Public-Key-Hash策略。
输入JSON：
```
 "inputs": [
    {
      "prev_hash": "fe469eb49c126419e24b88504902447a1d365ab428702fbe20d5d7444485dc8a",
      "output_index": 0,
      "output_value": 26694232,
      "sequence": 4294967295,
      "addresses": [
        "tb1q9z8m6pg9rdvvs5fc7amh7cpx09nx37sqwnvjee"
      ],
      "script_type": "pay-to-witness-pubkey-hash",
      "age": 0,
      "witness": [
        "30440220698481f25aa5265b59363a2d381f804f76a7d25b42ca4b788d45ad1880e9515d02204f54754e6eaca8cfd961fcba98b0d2f842f01179803b6271dc3f602e7f1a0b8a01",
        "02b9af5bd28475739238b9c99b7033547ad1fad2268c85e9675c4df6cafe57a815"
      ]
    }
  ],
```
交易输入结构：  
![图片](https://user-images.githubusercontent.com/105708747/181671903-bad331f0-8cbe-4517-8fe2-30efb39ed3fc.png)  
此处引用https://www.jianshu.com/p/5b0f42c62d97
### output分析
通过分析output包含信息可以发现，其共有两笔输出。在第一笔输出中，值为26668173，地址为tb1qj45pxpa4p22d4mlejx3jy022hnd43ua6jrjn3m。从script_type可以看出这不是一笔标准的 Pay-to-Public-Key-Hash (P2PKH) 交易类型，而使用隔离见证策略存在一个witness的Pay-to-Witness-Public-Key-Hash策略。而在第二笔输出中，其值为25914，地址为mkHS9ne12qx9pS9VojpwU5xtRd4T7X7ZUt，通过script_type可以看出这是一笔标准的 Pay-to-Public-Key-Hash (P2PKH) 交易类型。
输出JSON：
```
"outputs": [
    {
      "value": 26668173,
      "script": "001495681307b50a94daeff991a3223d4abcdb58f3ba",
      "addresses": [
        "tb1qj45pxpa4p22d4mlejx3jy022hnd43ua6jrjn3m"
      ],
      "script_type": "pay-to-witness-pubkey-hash"
    },
    {
      "value": 25914,
      "script": "76a914344a0f48ca150ec2b903817660b9b68b13a6702688ac",
      "addresses": [
        "mkHS9ne12qx9pS9VojpwU5xtRd4T7X7ZUt"
      ],
      "script_type": "pay-to-pubkey-hash"
    }
  ]
```
交易输出结构：  
![图片](https://user-images.githubusercontent.com/105708747/181672563-9a35dfbb-b1a0-478e-9fd1-19ee8e5274b3.png)  
此处引用https://www.jianshu.com/p/5b0f42c62d97
### 区块头分析
首先分析区块头部分，此处在blockchain中选择一个区块头进行分析。区块头中包含有整个区块中的信息，比如哈希值（hash），版本（ver），前个区块哈希（prev_block）,Merkle root哈希（mrkl_root），下个区块哈希（next_hash），时间戳、Nonce挖矿随机数等等。具体表示如下：  
![图片](https://user-images.githubusercontent.com/105708747/181510219-5dbedb2f-9fb7-4210-ab71-8d2608fd5569.png)
