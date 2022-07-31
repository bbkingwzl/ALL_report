# SM4_optimization
此处直接使用课内实验所写代码，分为查表优化、SIMD指令集加速以及多线程优化。这里代码为课内小组实验内容，此处直接使用。
## 运行解释以及注意事项
运行代码时直接下载c文件运行即可。  
由于当时本代码为小组实验所得，因此可能会与郭灿林、李岱耕小组代码重合，这里作出必要解释，课内实验代码为我们合力编写。  
另外是本次代码上传时间为多天前，但由于需要重新上传至总库因此时间改变，具体实现时间为2022-7-19： 
![图片](https://user-images.githubusercontent.com/105708747/180763614-df5873cc-9c08-414f-9c59-ad8bd7e14e73.png)
## 查表优化
查表方法的核心思想是将密码算法轮函数中尽可能多的变换操作制成表。SM4加/解密轮函数中的T变换由非线性变换τ和线性变换L构成。将非线性变换τ的输入记为X=(x0,x1,x2,x3)$\in$(Z28)4，输出记为Y=(y0,y1,y2,y3)$\in$(Z28)4。可将非线性变换$\tau$的操作定义如下。  
$\[{y_i} = Sbox({x_i}),0 \le i < 4\]$  
将线性变换L的输入记为$P=(p_0,p_1,...,p_{n-1}))\in (\mathbb{Z}_{2}^{m})^4$，输出记为$Q=(q_0,q_1,...,q_{n-1}))\in(\mathbb{Z}_{2}^{m})^4$。其中，m大小需为SM4使用S盒规模的倍数，m与n的关系满足n=32/m。由于L中仅包含循环移位和异或操作。因此，可将线性变换L的操作定义为下式：  
![图片](https://user-images.githubusercontent.com/105708747/179983581-7ab5a485-97be-4055-925e-467a58d3d6fa.png)  
m和n有多种取法，由参考文献结果可知，当m=8，n=8时，SM4性能最佳。
制表操作如下：
![图片](https://user-images.githubusercontent.com/105708747/179983798-ab5aee79-c42e-4165-9f0b-5904e3e6d71b.png)  
核心代码：  
```c
void S_boxes_init() {
    for (int i = 0; i < 256; i++) {
        uint32_t b = S_box[i] ^ S_box[i] << 2 ^ S_box[i] << 10 ^ S_box[i] << 18 ^ S_box[i] << 24;
        S_boxes_0[i] = b;
        S_boxes_1[i] = ROL(b, 010);
        S_boxes_2[i] = ROL(b, 020);
        S_boxes_3[i] = ROL(b, 030);
    }
    S_boxes_inited = 1;
}
```
```c
void SM4_encrypt(const uint32_t rk[32], const uint32_t X[4], uint32_t Y[4]) {
	uint32_t T[36] = {X[0], X[1], X[2], X[3]};
	for (int i = 0; i < 32; i++) {
		uint32_t a = T[i + 1] ^ T[i + 2] ^ T[i + 3] ^ rk[i];
		T[i + 4] = T[i] ^ S_boxes_0[a & 0xff] ^ S_boxes_1[a >> 010 & 0xff] ^ S_boxes_2[a >> 020 & 0xff] ^ S_boxes_3[a >> 030 & 0xff];
	}
	Y[0] = T[35];
	Y[1] = T[34];
	Y[2] = T[33];
	Y[3] = T[32];
}
```
## SIMD指令集加速
由于本文使用的是AVX2指令集，支持256位寄存器，但是加密一次只用128位，因此用SIMD指令集去优化的话，最小加密长度是128 * 8位，即1024位，这样才能把寄存器填满，充分利用SIMD寄存器。利用以下方式装载，每一列是每一组128bit明文，然后每一列分别进行迭代，这样就可以利用寄存器并行处理8组加密了。
```c
__m256i mmT[4] = {
	_mm256_set_epi32(X[0x00], X[0x04], X[0x08], X[0x0c], X[0x10], X[0x14], X[0x18], X[0x1c]),
	_mm256_set_epi32(X[0x01], X[0x05], X[0x09], X[0x0d], X[0x11], X[0x15], X[0x19], X[0x1d]),
	_mm256_set_epi32(X[0x02], X[0x06], X[0x0a], X[0x0e], X[0x12], X[0x16], X[0x1a], X[0x1e]),
	_mm256_set_epi32(X[0x03], X[0x07], X[0x0b], X[0x0f], X[0x13], X[0x17], X[0x1b], X[0x1f]),
};
```
后面则是把原来的异或、移位、与、查表操作别分替换成AVX2指令集中的$\_$mm256$\_$xor$\_$si256(),$\_$mm256$\_$srli$\_$epi32(),$\_$mm256$\_$and$\_$si256(),$\_$mm256$\_$i32gather$\_$epi32().  
```c
void encrypt(const uint32_t X[32], uint32_t Y[32]){
    const __m256i mm0xff = _mm256_set_epi32(0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff);
    __m256i mmT[4] = {
        _mm256_set_epi32(X[0x00], X[0x04], X[0x08], X[0x0c], X[0x10], X[0x14], X[0x18], X[0x1c]),
        _mm256_set_epi32(X[0x01], X[0x05], X[0x09], X[0x0d], X[0x11], X[0x15], X[0x19], X[0x1d]),
        _mm256_set_epi32(X[0x02], X[0x06], X[0x0a], X[0x0e], X[0x12], X[0x16], X[0x1a], X[0x1e]),
        _mm256_set_epi32(X[0x03], X[0x07], X[0x0b], X[0x0f], X[0x13], X[0x17], X[0x1b], X[0x1f]),
    };
    for (int i = 0; i < 32;) {
        __m256i mma;
        mma = _mm256_xor_si256(_mm256_xor_si256(mmT[1], mmT[2]), _mm256_xor_si256(mmT[3], mmrk[i++]));
        mmT[0] = _mm256_xor_si256(mmT[0], _mm256_xor_si256(
            _mm256_xor_si256(
                _mm256_i32gather_epi32(S_boxes_0, _mm256_and_si256(mma, mm0xff), 4),
                _mm256_i32gather_epi32(S_boxes_1, _mm256_and_si256(_mm256_srli_epi32(mma, 010), mm0xff), 4)
            ),
            _mm256_xor_si256(
                _mm256_i32gather_epi32(S_boxes_2, _mm256_and_si256(_mm256_srli_epi32(mma, 020), mm0xff), 4),
                _mm256_i32gather_epi32(S_boxes_3, _mm256_srli_epi32(mma, 030), 4)
            )
        ));
        mma = _mm256_xor_si256(_mm256_xor_si256(mmT[2], mmT[3]), _mm256_xor_si256(mmT[0], mmrk[i++]));
        mmT[1] = _mm256_xor_si256(mmT[1], _mm256_xor_si256(
            _mm256_xor_si256(
                _mm256_i32gather_epi32(S_boxes_0, _mm256_and_si256(mma, mm0xff), 4),
                _mm256_i32gather_epi32(S_boxes_1, _mm256_and_si256(_mm256_srli_epi32(mma, 010), mm0xff), 4)
            ),
            _mm256_xor_si256(
                _mm256_i32gather_epi32(S_boxes_2, _mm256_and_si256(_mm256_srli_epi32(mma, 020), mm0xff), 4),
                _mm256_i32gather_epi32(S_boxes_3, _mm256_srli_epi32(mma, 030), 4)
            )
        ));
        mma = _mm256_xor_si256(_mm256_xor_si256(mmT[3], mmT[0]), _mm256_xor_si256(mmT[1], mmrk[i++]));
        mmT[2] = _mm256_xor_si256(mmT[2], _mm256_xor_si256(
            _mm256_xor_si256(
                _mm256_i32gather_epi32(S_boxes_0, _mm256_and_si256(mma, mm0xff), 4),
                _mm256_i32gather_epi32(S_boxes_1, _mm256_and_si256(_mm256_srli_epi32(mma, 010), mm0xff), 4)
            ),
            _mm256_xor_si256(
                _mm256_i32gather_epi32(S_boxes_2, _mm256_and_si256(_mm256_srli_epi32(mma, 020), mm0xff), 4),
                _mm256_i32gather_epi32(S_boxes_3, _mm256_srli_epi32(mma, 030), 4)
            )
        ));
        mma = _mm256_xor_si256(_mm256_xor_si256(mmT[0], mmT[1]), _mm256_xor_si256(mmT[2], mmrk[i++]));
        mmT[3] = _mm256_xor_si256(mmT[3], _mm256_xor_si256(
            _mm256_xor_si256(
                _mm256_i32gather_epi32(S_boxes_0, _mm256_and_si256(mma, mm0xff), 4),
                _mm256_i32gather_epi32(S_boxes_1, _mm256_and_si256(_mm256_srli_epi32(mma, 010), mm0xff), 4)
            ),
            _mm256_xor_si256(
                _mm256_i32gather_epi32(S_boxes_2, _mm256_and_si256(_mm256_srli_epi32(mma, 020), mm0xff), 4),
                _mm256_i32gather_epi32(S_boxes_3, _mm256_srli_epi32(mma, 030), 4)
            )
        ));
    }
    uint32_t T_0[8], T_1[8], T_2[8], T_3[8];
    _mm256_storeu_si256((__m256i *)T_0, mmT[0]);
    _mm256_storeu_si256((__m256i *)T_1, mmT[1]);
    _mm256_storeu_si256((__m256i *)T_2, mmT[2]);
    _mm256_storeu_si256((__m256i *)T_3, mmT[3]);
    Y[0x00] = T_3[7];Y[0x04] = T_3[6];Y[0x08] = T_3[5];Y[0x0c] = T_3[4];Y[0x10] = T_3[3];Y[0x14] = T_3[2]; Y[0x18] = T_3[1];Y[0x1c] = T_3[0];Y[0x01] = T_2[7];Y[0x05] = T_2[6];Y[0x09] = T_2[5];Y[0x0d] = T_2[4];Y[0x11] = T_2[3];Y[0x15] = T_2[2];Y[0x19] = T_2[1]; Y[0x1d] = T_2[0];Y[0x02] = T_1[7];Y[0x06] = T_1[6]; Y[0x0a] = T_1[5];Y[0x0e] = T_1[4];Y[0x12] = T_1[3];Y[0x16] = T_1[2]; Y[0x1a] = T_1[1]; Y[0x1e] = T_1[0];Y[0x03] = T_0[7];Y[0x07] = T_0[6];Y[0x0b] = T_0[5];Y[0x0f] = T_0[4];Y[0x13] = T_0[3]; Y[0x17] = T_0[2];Y[0x1b] = T_0[1];Y[0x1f] = T_0[0];
}
```
## 多线程实现
SM4内部算法是迭代型的，因此在单组加密算法里实现多线程意义不大，因此我们考虑的是加密多组明文的情况，即从提高吞吐量的角度优化。多线程思路和之前向量求和是类似的，出于简化的角度考虑，我们采用ECB加密模式，加解密都可以并行处理。  
核心代码：
```c
void *threading(void *pbuf) {
	uint32_t *plaintext = ((args_t *)pbuf)->plaintext, *rk = ((args_t *)pbuf)->rk, *ciphertext = ((args_t *)pbuf)->ciphertext, *end = ((args_t *)pbuf)->end;
	char mode = ((args_t *)pbuf)->mode;
	while(plaintext < end){
		if (mode == 1) SM4_encrypt(rk, plaintext, ciphertext);
		else SM4_decrypt(rk, ciphertext, plaintext);
		plaintext += 4;
		ciphertext += 4;
	}
	return NULL;
}
```
## 结果展示
时间开销对比：  
![图片](https://user-images.githubusercontent.com/105708747/180763245-5c4e2440-2cff-430e-856a-c236468ea502.png)
![图片](https://user-images.githubusercontent.com/105708747/180763300-c46bfeb5-43c9-4f73-9e1e-4844c4ae29ac.png)  
利用 linux 下的 gprof 工具，生成 gmon.out 文件，可以分析程序运行过程各个函数调用的次数和时间。  
![图片](https://user-images.githubusercontent.com/105708747/180763378-86c06826-95a9-4c49-8557-cdfb265bc2c1.png)

