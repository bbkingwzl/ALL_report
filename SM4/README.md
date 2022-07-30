# SM4
本次实验实现了SM4的ECB模式以及CBC模式，本次实验为笔者独自完成。引用部分在文中有所展示。
## 运行解释以及注意事项
在下载完毕所提供的文件后，直接运行SM4.cpp即可。
## ECB模式算法实现
对于普遍的遍历实现方式，无论是在密钥扩展算法中或是加密算法中，对于三十二轮中的每一轮来说都会存在一个 32 长的中间数组存储 K 或 X，而这将会增大空间开销，并且访问数组的速度慢于访问普通变量的速度，因此在具体的实现过程中将对此方面进行优化。   
具体的优化实现方式为，区别于传统方式，对于密钥扩展算法以及加密算法的中间变量仅开辟四个内存空间使用强制类型转换即以四个变量进行承接。对于 32 轮的 for 循环，将其改变为仅进行 8 次 for 循环而对于每次内层循环而言，每次进行四次运算，每次将中间变量的值与 rk 或 x 进行替换，以此节省空间开销以及时间开销。核心代码实现如下：
```c
void SM4_Enc_Dec(uint8_t* input, uint8_t* output, uint32_t *rk)
{
	uint32_t x0, x1, x2, x3;
	uint32_t* temp;
	temp = (uint32_t*)input;
	x0 = temp[0];
	x1 = temp[1];
	x2 = temp[2];
	x3 = temp[3];
#ifdef LITTLE_ENDIAN
	x0 = remove(x0, 16); x0 = ((x0 & 0x00FF00FF) << 8) ^ ((x0 & 0xFF00FF00) >> 8);
	x1 = remove(x1, 16); x1 = ((x1 & 0x00FF00FF) << 8) ^ ((x1 & 0xFF00FF00) >> 8);
	x2 = remove(x2, 16); x2 = ((x2 & 0x00FF00FF) << 8) ^ ((x2 & 0xFF00FF00) >> 8);
	x3 = remove(x3, 16); x3 = ((x3 & 0x00FF00FF) << 8) ^ ((x3 & 0xFF00FF00) >> 8);
#endif
	for (int i = 0; i < 32; i += 4)
	{
		uint32_t mid_x = x1 ^ x2 ^ x3 ^ rk[i];
		mid_x = ByteSub(mid_x);
		x0 ^= Lun_last(mid_x);
		mid_x = x2 ^ x3 ^ x0 ^ rk[i + 1];
		mid_x = ByteSub(mid_x);
		x1 ^= Lun_last(mid_x);
		mid_x = x3 ^ x0 ^ x1 ^ rk[i + 2];
		mid_x = ByteSub(mid_x);
		x2 ^= Lun_last(mid_x);
		mid_x = x2 ^ x0 ^ x1 ^ rk[i + 3];
		mid_x = ByteSub(mid_x);
		x3 ^= Lun_last(mid_x);
	}
#ifdef LITTLE_ENDIAN
	x0 = remove(x0, 16); x0 = ((x0 & 0x00FF00FF) << 8) ^ ((x0 & 0xFF00FF00) >> 8);
	x1 = remove(x1, 16); x1 = ((x1 & 0x00FF00FF) << 8) ^ ((x1 & 0xFF00FF00) >> 8);
	x2 = remove(x2, 16); x2 = ((x2 & 0x00FF00FF) << 8) ^ ((x2 & 0xFF00FF00) >> 8);
	x3 = remove(x3, 16); x3 = ((x3 & 0x00FF00FF) << 8) ^ ((x3 & 0xFF00FF00) >> 8);
#endif
	temp = (uint32_t*)output;
	temp[0] = x3;
	temp[1] = x2;
	temp[2] = x1;
	temp[3] = x0;
}
```
## CBC模式算法实现
CBC 模式主要基于两种思想，第一，所有分组的加密都链接在一起，其中各分组所用的密钥相同。加密时输入的是当前的明文分组和上一个密文分组的异或，这样使得密文分组不仅依赖当前明文
分组，而且还依赖前面所有的明文分组。因此，加密算法的输入不会显示出与这次的明文分组之间的固定关系，所以重复的明文分组不会再密文中暴露出这种重复关系。第二，加密过程使用初始量进行了随机化。基于在 1.2 中所实现的 SM4 加解密算法，便可很容易的实现 CBC 模式加密，具体核心代码如下所示：
```c
void SM4_CBC(uint8_t* In, uint8_t* Out, uint8_t* iv, uint32_t length,int flag, uint32_t* rk)
{
	uint8_t* temp_in = In;
	uint8_t* temp_out = Out;
	uint8_t temp_temp_in[SM4_BLOCK_SIZE] = { 0 };
	uint8_t temp_temp_out[SM4_BLOCK_SIZE] = { 0 };
	uint8_t temp_iv[SM4_BLOCK_SIZE] = {0};
	memcpy(temp_iv, iv, SM4_BLOCK_SIZE);
	if (flag == ENC)
	{
		while (length >= SM4_BLOCK_SIZE)
		{
			for (int i = 0; i < SM4_BLOCK_SIZE; i++)
				temp_temp_in[i] = temp_in[i] ^ temp_iv[i];
			SM4_Enc_Dec(temp_temp_in, temp_out, rk);
			memcpy(temp_iv, temp_out, SM4_BLOCK_SIZE);
			length -= SM4_BLOCK_SIZE;
			temp_in += SM4_BLOCK_SIZE;
			temp_out += SM4_BLOCK_SIZE;
		}
	}
	else
	{
		while (length >= SM4_BLOCK_SIZE)
		{
			SM4_Enc_Dec(temp_in, temp_temp_out, rk);

			for (int i = 0; i < SM4_BLOCK_SIZE; i++)
				temp_out[i] = temp_temp_out[i] ^ temp_iv[i];

			memcpy(temp_iv, temp_in, SM4_BLOCK_SIZE);
			length -= SM4_BLOCK_SIZE;
			temp_in += SM4_BLOCK_SIZE;
			temp_out += SM4_BLOCK_SIZE;
		}
	}
}
```
## ECB模式与CBC模式效率对比
当数据规模较小时，无论使用何种模式其时间开销均较小，因此本文采用适当的数据规模对两种加密模式进行对比。加密时间结果对比如下：  
![图片](https://user-images.githubusercontent.com/105708747/181924687-1dfa0dca-a6ac-45e5-b66e-67960d71599f.png)  
由上图可知，两种加密模式效率基本一致，CBC 模式效率会略低于 ECB 模式，这是由于 iv 的更新以及 iv 与明密文的异或操作会增加时间开销，但影响并不太大。
## 打印结果展示
![图片](https://user-images.githubusercontent.com/105708747/181924760-e26db88e-b183-46a7-ba7a-c91b01336bcd.png)
