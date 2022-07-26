#include <stdlib.h>
#include <string.h>
#include<stdint.h>
#include <stdio.h>
#include<intrin.h>
#include<emmintrin.h>

#define FF0(X, Y, Z) ( (X) ^ (Y) ^ (Z) )
#define FF1(X, Y, Z) ( ((X)&(Y)) | ((X)&(Z)) | ((Y)&(Z)) )
#define GG0(X, Y, Z) ( (X) ^ (Y) ^ (Z) )
#define GG1(X, Y, Z) ( ((X)&(Y)) | ((~(X))&(Z)) )
#define remove_bit(X, cnt)  ( ( (X)<<((cnt)&31) ) | ( (X)>>(32-((cnt)&31)) ) )
#define P0(X)		 ( (X) ^ remove_bit(X,  9) ^ remove_bit(X, 17))
#define P1(X)		 ( (X) ^ remove_bit(X, 15) ^ remove_bit(X, 23))

uint8_t output[64] = { 0 };
uint32_t IV[8] = { 0x7380166f ,0x4914b2b9 ,0x172442d7 ,0xda8a0600 ,0xa96f30bc ,0x163138aa ,0xe38dee4d ,0xb0fb0e4e };
uint32_t T[64] = { 0 };



__m128i shift_left(__m128i a, int k)
{
	__m128i reg2, reg3, reg4;
	/*初始化128位整数为全一，即用四个4个32位全一整数来构造*/
	__m128i reg1 = _mm_set_epi32(0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF);
	k = k % 32;
	/*将a左移k位与reg1相与存入reg2中*/
	reg2 = _mm_and_si128(reg1, _mm_slli_epi32(a, k));
	/*将reg1与a相与的结果右移32-k位存入reg3中*/
	reg3 = _mm_srli_epi32(_mm_and_si128(reg1, a), 32 - k);
	/*reg2与reg3进行或操作*/
	reg4 = _mm_or_si128(reg2, reg3);
	return reg4;
}

uint32_t FF(uint32_t X, uint32_t Y, uint32_t Z, int i)
{
	uint32_t res = 0;
	if (0 <= i && i < 16)
		FF0(X, Y, Z);
	else if (16 <= i && i < 64)
		FF1(X, Y, Z);
	return res;
}


uint32_t GG(uint32_t X, uint32_t Y, uint32_t Z, int i)
{
	uint32_t ret = 0;
	if (0 <= i && i < 16)
	{
		GG0(X, Y, Z);
	}
	else if (16 <= i && i < 64)
	{
		GG1(X, Y, Z);
	}
	return ret;
}

void CF(uint8_t* text)
{
	/*利用SIMD加速消息扩展过程*/
	int j;

	__m128i res1[17];
	__m128i reg1, reg2, reg3, reg4, reg5, reg6, reg7, reg8, reg9, reg10;

	/*按照字节划分，将text的每8bit划归到res1中，每128bit进行一次存储*/
	res1[1] = _mm_setr_epi8(text[19], text[18], text[17], text[16], text[23], text[22], text[21], text[20], text[27], text[26], text[25], text[24], text[31], text[30], text[29], text[28]);
	res1[2] = _mm_setr_epi8(text[35], text[34], text[33], text[32], text[39], text[38], text[37], text[36], text[43], text[42], text[41], text[40], text[47], text[46], text[45], text[44]);
	res1[3] = _mm_setr_epi8(text[51], text[50], text[49], text[48], text[55], text[54], text[53], text[52], text[59], text[58], text[57], text[56], text[63], text[62], text[61], text[60]);

	int W[68];
	//计算W[0]--W[15]
	for (j = 0; j < 16; j++)
		W[j] = text[j * 4 + 0] << 24 | text[j * 4 + 1] << 16 | text[j * 4 + 2] << 8 | text[j * 4 + 3];

	/*设置各128位reg的值，以便于SIMD优化。设置完毕后，计算W[16]--W[67]*/
	__m128i res2 = _mm_set_epi32(0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF);
	for (j = 4; j < 17; j++)
	{
		reg10 = _mm_setr_epi32(W[j * 4 - 16], W[j * 4 - 15], W[j * 4 - 14], W[j * 4 - 13]);;
		reg4 = _mm_setr_epi32(W[j * 4 - 13], W[j * 4 - 12], W[j * 4 - 11], W[j * 4 - 10]);
		reg5 = _mm_setr_epi32(W[j * 4 - 9], W[j * 4 - 8], W[j * 4 - 7], W[j * 4 - 6]);
		reg6 = _mm_setr_epi32(W[j * 4 - 3], W[j * 4 - 2], W[j * 4 - 1], 0);
		reg7 = _mm_setr_epi32(W[j * 4 - 6], W[j * 4 - 5], W[j * 4 - 4], W[j * 4 - 3]);
		reg1 = _mm_xor_si128(reg10, reg5);
		reg2 = shift_left(reg6, 15);
		reg1 = _mm_xor_si128(reg1, reg2);
		reg3 = _mm_xor_si128(reg1, _mm_xor_si128(shift_left(reg1, 15), shift_left(reg1, 23)));
		reg8 = _mm_xor_si128(shift_left(reg4, 7), reg7);
		res1[j] = _mm_xor_si128(reg3, reg8);
		_mm_maskstore_epi32(&W[j * 4], res2, res1[j]);
		W[j * 4] = P1(W[j * 4 - 16] ^ W[j * 4 - 9] ^ (remove_bit(W[j * 4 - 3], 15))) ^ (remove_bit(W[j * 4 - 13], 7)) ^ W[j * 4 - 6];
	}

	uint32_t W1[64];
	for (j = 0; j < 64; j++)
		W1[j] = W[j] ^ W[j + 4];

	uint32_t A, B, C, D, E, F, G, H;
	A = IV[0];
	B = IV[1];
	C = IV[2];
	D = IV[3];
	E = IV[4];
	F = IV[5];
	G = IV[6];
	H = IV[7];

	uint32_t SS1, SS2, TT1, TT2;
	for (j = 0; j < 64; j++)
	{
		SS1 = remove_bit(((remove_bit(A, 12)) + E + (remove_bit(T[j], j))) & 0xFFFFFFFF, 7);
		SS2 = SS1 ^ (remove_bit(A, 12));
		TT1 = (FF(A, B, C, j) + D + SS2 + W1[j]) & 0xFFFFFFFF;
		TT2 = (GG(E, F, G, j) + H + SS1 + W[j]) & 0xFFFFFFFF;
		D = C;
		C = remove_bit(B, 9);
		B = A;
		A = TT1;
		H = G;
		G = remove_bit(F, 19);
		F = E;
		E = P0(TT2);

	}

	IV[0] = (A ^ IV[0]);
	IV[1] = (B ^ IV[1]);
	IV[2] = (C ^ IV[2]);
	IV[3] = (D ^ IV[3]);
	IV[4] = (E ^ IV[4]);
	IV[5] = (F ^ IV[5]);
	IV[6] = (G ^ IV[6]);
	IV[7] = (H ^ IV[7]);
}

void SM3_r(uint8_t* text, uint32_t len) {

	int i;

	/*将text传入output中，并执行压缩函数的迭代过程（注意此处应该除以64，这是因为每次以512bit为一次运算，剩余不能整除部分将会后续处理）*/
	for (i = 0; i < len / 64; i++) {
		memcpy(output, text + i * 64, 64);
		CF(output);
	}

	uint64_t len_bit = len * 8;//将len转为以bit为单位

	/*此处为不能被64整除的部分，即不足512bit的剩余部分*/
	int rest = len % 64;
	memset(&output[rest], 0, 64 - rest);
	memcpy(output, text + i * 64, rest);

	/*由于最后一部分不足512bit，需要对最后一部分进行填充，填充完毕后再进行压缩*/
	output[rest] = 0x80;
	if (rest <= 55) {
		for (i = 0; i < 8; i++)
			output[56 + i] = (len_bit >> ((8 - 1 - i) * 8)) & 0xFF;
		CF(output);
	}
	else {
		CF(output);
		memset(output, 0, 64);
		for (i = 0; i < 8; i++)
			output[56 + i] = (len_bit >> ((8 - 1 - i) * 8)) & 0xFF;
		CF(output);
	}

}
int main()
{
	int i = 0;
	for (i = 0; i < 16; i++)
	{
		T[i] = 0x79cc4519;
	}
	for (i = 16; i < 64; i++)
	{
		T[i] = 0x7a879d8a;
	}
	uint8_t str1[] = "bbkingwzlbbkingwzlbbkingwzlbbkingwzlbbkingwzlbbkingwzlbbkingwzl";
	SM3_r(str1, 64);
	printf("SM3Enc result :");
	for (int i = 0; i < 8; i++)
		printf("%x ", IV[i]);
	return 0;
}
