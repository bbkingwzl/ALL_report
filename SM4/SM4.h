#ifndef HEADER_SM4_H
#define HEADER_SM4_H

#ifdef  __cplusplus
extern "C" {
#endif

	typedef unsigned char muint8;
	typedef unsigned long muint32;

#define LITTLE_ENDIAN     //定义小端字节序
	//#define BIG_ENDIAN     //定义大端字节序
#define SM4_ENCRYPT  0     //定义加密标志
#define SM4_DECRYPT  1     //定义解密标志

#define SM4_BLOCK_LEN	16
#define SM4_KEY_LEN	16
#define SM4_IV_LEN	SM4_BLOCK_LEN

// SM4的密钥扩展算法
// 参数说明：Key为加密密钥，rk为子密钥，CryptFlag为加解密标志
	int SM4KeyExt(const muint8* Key, muint32* rk, muint32 CryptFlag);

	// SM4的加解密函数
	// 参数说明：Input为输入信息分组，Output为输出分组，rk为轮密钥
	int SM4Crypt(const muint8* Input, muint8* Output, const muint32* rk);

	//For EVP
	void sm4_set_key(muint32* rk, const unsigned char* data, int enc);
	void sm4_ecb_encrypt(const unsigned char* in, unsigned char* out, const muint32* rk,
		int enc);
	void sm4_cbc_encrypt(const unsigned char* in, unsigned char* out, long length,
		const muint32* rk, unsigned char* iv, int enc);
	void sm4_cfb64_encrypt(const unsigned char* in, unsigned char* out,
		long length, const muint32* rk, unsigned char* ivec,
		int* num, int enc);
	void sm4_ofb64_encrypt(const unsigned char* in, unsigned char* out,
		long length, const muint32* rk, unsigned char* ivec,
		int* num);

#ifdef  __cplusplus
}
#endif

#endif
