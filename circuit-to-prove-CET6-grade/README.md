# -circuit-to-prove-CET6-grade
Write a circuit to prove that your CET6 grade is larger than 425. a. Your grade info is like (cn_id, grade, year, sig_by_moe). These grades are published as commitments onchain by MoE.本次实验为笔者独自完成。引用部分在文中有所展示。
# 运行说明
本次实验以示例的形式完成，其中wzl文件夹中便是一个示例。其余两个文件分别为电路文件以及输入文件，详见本报告中的信息。本次实验运行过程较为繁琐，因此将对运行过程进行一个完整的阐述。
## 准备工作
### 安装Node(如果已经安装请跳过)
```
sudo apt update
sudo apt install nodejs npm -y
node --version
```
这里显示node的版本，必须保证node版本大于12.若在查看node版本时小于12，请按照如下步骤进行更新。
```
npm cache clean -f
sudo npm install -g n
sudo n latest
```
### 安装Rust(如果已经安装请跳过)
```
sudo apt install curl -y
sudo apt install cmake build-essential -y
curl --proto '=https' --tlsv1.2 https://sh.rustup.rs -sSf | sh
```
### 安装Circom(如果已经安装请跳过)
```
git clone https://github.com/iden3/circom.git
cd circom
source $HOME/.cargo/env
cargo build --release
```
Rust社区公开的第三方包都集中在crates.io网站上面，他们的文档被自动发布到doc.rs网站上。Rust提供了非常方便的包管理器cargo，它类似于Node.js的npm和Python的pip。但cargo不仅局限于包管理，还为Rust生态系统提供了标准的工作流。
在实际开发中，为了更快速下载第三方包，我们需要把crates.io换国内的镜像源，否则在拉取 crates.io 仓库代码会非常慢，Updating crates.io index 卡很久，很多次超时导致引用库没法编译。  
在 $HOME/.cargo/config 中添加如下内容：
```
# 放到 `$HOME/.cargo/config` 文件中
[source.crates-io]
#registry = "https://github.com/rust-lang/crates.io-index"

# 替换成你偏好的镜像源
replace-with = 'ustc'
#replace-with = 'sjtu'

# 清华大学
[source.tuna]
registry = "https://mirrors.tuna.tsinghua.edu.cn/git/crates.io-index.git"

# 中国科学技术大学
[source.ustc]
registry = "git://mirrors.ustc.edu.cn/crates.io-index"

# 上海交通大学
[source.sjtu]
registry = "https://mirrors.sjtug.sjtu.edu.cn/git/crates.io-index"

# rustcc社区
[source.rustcc]
registry = "git://crates.rustcc.cn/crates.io-index"
```
### 更新Circom
```
cargo install --path circom
circom --help
```
### 安装Snarkjs(如果已经安装请跳过)
```
sudo npm install -g snarkjs
```
## 计算和证明
### 设计电路
这里参照基于circom、snarkjs实现零知识证明不透漏具体地理位置的区域监控的示例进行编写。  
```c
template Main() {
    signal input CETRange[2];
 
    signal input CETScore;
 
    signal output out;
 
    component gt1 = GreaterEqThan(10);
    gt1.in[0] <== CETScore;
    gt1.in[1] <== CETRange[0];
    gt1.out === 1;
}
 
template GreaterEqThan(n) {
    signal input in[2];
    signal output out;
 
    component lt = LessThan(n);
 
    lt.in[0] <== in[1];
    lt.in[1] <== in[0]+1;
    lt.out ==> out;
}
 
template LessThan(n) {
    assert(n <= 252);
    signal input in[2];
    signal output out;
 
    component n2b = Num2Bits(n+1);
 
    n2b.in <== in[0]+ (1<<n) - in[1];
 
    out <== 1-n2b.out[n];
}
 
template Num2Bits(n) {
    signal input in;
    signal output out[n];
    var lc1=0;
 
    var e2=1;
    for (var i = 0; i<n; i++) {
        out[i] <-- (in >> i) & 1;
        out[i] * (out[i] -1 ) === 0;
        lc1 += out[i] * e2;
        e2 = e2+e2;
    }
 
    lc1 === in;
}
 
component main = Main();
```
### 编译电路
执行如下命令进行编译
```
circom InRange.circom --r1cs --wasm --sym
```
执行成功后，会生成如下截图的文件：  
![图片](https://user-images.githubusercontent.com/105708747/181920028-3602c84b-5327-4ca6-8858-087fad902f8f.png)
### 设计输入
设计电路的输入是下一步计算证明的必要前提，在相同目录下新建input.json输入文件，编写如下输入，本案例中即CET6的成绩合格范围[425,710]以及笔者实际的CET6成绩610：
```c
{
    "CETRange": [ 425, 710],
    "CETScore":  610
}
```
### 计算获得证据(Computing the witness)
利用WebAssembly计算证据，即执行如下命令：
```
node generate_witness.js InRange.wasm ../input.json ../witness.wtns
```
该命令会输出witness.wtns，下一步运算需要用到。
### 证明电路(Proving circuits with zk)
#### Phase1: Powers of Tau
First, we start a new "powers of tau" ceremony，即执行如下命令，生成 pot12_0000.ptau
```
snarkjs powersoftau new bn128 12 pot12_0000.ptau -v
```
Then, we contribute to the ceremony，即执行如下命令，生成pot12_0001.ptau，此处会提示输入随机字符，随意输入即可。
```
snarkjs powersoftau contribute pot12_0000.ptau pot12_0001.ptau --name="First contribution" -v
```
#### Phase2: circuit-specific
start the generation of this phase，即执行如下命令，生成pot12_final.ptau
```
snarkjs powersoftau prepare phase2 pot12_0001.ptau pot12_final.ptau -v
```
Next，we generate a .zkey file that will contain the proving and verification keys together with all phase 2 contributions.即执行如下命令，生成
```
snarkjs groth16 setup InRange.r1cs pot12_final.ptau multiplier2_0000.zkey
```
Contribute to the phase 2 of the ceremony，即执行如下命令：
```
snarkjs zkey contribute multiplier2_0000.zkey multiplier2_0001.zkey --name="1st Contributor Name" -v\
```
Export the verification key，执行如下命令:
```
snarkjs zkey export verificationkey multiplier2_0001.zkey verification_key.json
```
#### Generating a Proof
Once the witness is computed and the trusted setup is already executed, we can generate a zk-proof associated to the circuit and the witness，即执行如下命令：
```
snarkjs groth16 prove multiplier2_0001.zkey witness.wtns proof.json public.json
```
#### Verifying a Proof
To verify the proof，执行如下命令：
```
snarkjs groth16 verify verification_key.json public.json proof.json
```
The command uses the files verification_key.json we exported earlier,proof.json and public.json to check if the proof is valid. If the proof is valid, the command outputs an OK.  
## 运行结果展示
最终证明输出结果截图如下：  
![图片](https://user-images.githubusercontent.com/105708747/181919958-0b476114-3f41-4224-b04c-54868fba9c53.png)
## 参考内容
[1]https://feeler.blog.csdn.net/article/details/124145767   
[2]https://blog.csdn.net/rznice/article/details/112424406   
[3]https://blog.csdn.net/m0_62598303/article/details/122768427
