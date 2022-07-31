# find-key
Find a key with hash value “sdu_cst_20220610” under a message composed of your name followed by your student ID. For example, “San Zhan 202000460001”.本次实验为笔者独自完成。引用部分在文中有所展示。
## 运行解释以及注意事项
在导入所给头文件后，直接运行ConsoleApplication32.cpp即可。编写头文件时引用https://github.com/cmuratori ，可能会有部分代码与他人重复，望见谅。
## find-key实现
### 准备工作
首先定义一系列SIMD指令集所用到的操作过程，此处引用https://github.com/cmuratori。
```c
#define Block_Size 4096

uint8_t MeowShiftAdjust[32] = { 0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 };
uint8_t MeowMaskLen[32] = { 255,255,255,255, 255,255,255,255, 255,255,255,255, 255,255,255,255, 0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0 };

#define movdqu_mem(A, B)  _mm_storeu_si128((__m128i *)(A), B)
#define movq(A, B) A = _mm_set_epi64x(0, B);
#define aesdec(A, B)  A = _mm_aesdec_si128(A, B)
#define pshufb(A, B)  A = _mm_shuffle_epi8(A, B)
#define pxor(A, B)    A = _mm_xor_si128(A, B)
#define paddq(A, B) A = _mm_add_epi64(A, B)
#define pand(A, B)    A = _mm_and_si128(A, B)
#define palignr(A, B, i) A = _mm_alignr_epi8(A, B, i)
#define pxor_clear(A, B)    A = _mm_setzero_si128(); 
#define MEOW_DUMP_STATE(...)
#define psubq(A, B) A = _mm_sub_epi64(A, B)
#define aesenc(A, B)  A = _mm_aesenc_si128(A, B)

#define MEOW_MIX_REG_inv(r1, r2, r3, r4, r5,  i1, i2, i3, i4) \
pxor(r4, i4);\
paddq(r5, i3); \
aesenc(r2, r4); \
_ReadWriteBarrier(); \
pxor(r2, i2); \
paddq(r3, i1); \
aesenc(r1, r2); \
_ReadWriteBarrier() 

#define MEOW_MIX_inv(r1, r2, r3, r4, r5,  ptr) \
MEOW_MIX_REG_inv(r1, r2, r3, r4, r5, _mm_loadu_si128( (__m128i *) ((ptr) + 15) ), _mm_loadu_si128( (__m128i *) ((ptr) + 0)  ), _mm_loadu_si128( (__m128i *) ((ptr) + 1)  ), _mm_loadu_si128( (__m128i *) ((ptr) + 16) ))

#define MEOW_SHUFFLE_inv(r1, r2, r3, r4, r5, r6) \
pxor(r2, r3);\
psubq(r5, r6); \
aesenc(r4, r2); \
pxor(r4, r6); \
psubq(r2, r5); \
aesenc(r1, r4)
```
### 打印函数
输入为一个128bit哈希值，将该哈希值按照32bit进行拆分打印。此处引用https://github.com/cmuratori。
```c
//打印
static void Print_Res(__m128i hash_val)
{
    printf("%08x%08x%08x%08x\n",
        _mm_extract_epi32(hash_val, 3),
        _mm_extract_epi32(hash_val, 2),
        _mm_extract_epi32(hash_val, 1),
        _mm_extract_epi32(hash_val, 0)
    );
}
```
### MeowHash_inv函数实现
此处过程较为繁琐，传入参数为哈希值，消息message以及其对应长度。这里定义的xmm0-xmm7 are the hash accumulation lanes； xmm8-xmm15 hold values to be appended (residual, length) 。将hash_value赋给xmm0，xmm1-xmm7自行取值而后将一个 128 位哈希分为八个通道，利用SIMD指令集相关操作运行，最终将结果进行打印。此处引用https://github.com/cmuratori。
```c
void MeowHash_inv(void* Hash_value, uint32_t Len, void* Message)
{
    __m128i xmm0, xmm1, xmm2, xmm3, xmm4, xmm5, xmm6, xmm7; 
    __m128i xmm8, xmm9, xmm10, xmm11, xmm12, xmm13, xmm14, xmm15; 

    uint8_t* rax = (uint8_t*)Message;
    uint8_t* rcx = (uint8_t*)Hash_value;


    xmm0 = _mm_loadu_si128((__m128i*)(rcx));
    xmm1 = _mm_loadu_si128((__m128i*)(rcx + 0x10));
    xmm2 = _mm_loadu_si128((__m128i*)(rcx + 0x20));
    xmm3 = _mm_loadu_si128((__m128i*)(rcx + 0x30));
    xmm4 = _mm_loadu_si128((__m128i*)(rcx + 0x40));
    xmm5 = _mm_loadu_si128((__m128i*)(rcx + 0x50));
    xmm6 = _mm_loadu_si128((__m128i*)(rcx + 0x60));
    xmm7 = _mm_loadu_si128((__m128i*)(rcx + 0x70));
    MEOW_DUMP_STATE("Seed_inv", xmm0, xmm1, xmm2, xmm3, xmm4, xmm5, xmm6, xmm7, 0);


    psubq(xmm4, xmm0);
    pxor(xmm1, xmm0);
    pxor(xmm5, xmm4);
    psubq(xmm2, xmm0);
    psubq(xmm3, xmm1);
    psubq(xmm6, xmm4);
    psubq(xmm7, xmm5);
    MEOW_DUMP_STATE("PostFold_inv", xmm0, xmm1, xmm2, xmm3, xmm4, xmm5, xmm6, xmm7, 0);



    MEOW_SHUFFLE_inv(xmm0, xmm1, xmm2, xmm4, xmm5, xmm6);
    MEOW_SHUFFLE_inv(xmm1, xmm2, xmm3, xmm5, xmm6, xmm7);
    MEOW_SHUFFLE_inv(xmm2, xmm3, xmm4, xmm6, xmm7, xmm0);
    MEOW_SHUFFLE_inv(xmm3, xmm4, xmm5, xmm7, xmm0, xmm1);
    MEOW_SHUFFLE_inv(xmm4, xmm5, xmm6, xmm0, xmm1, xmm2);
    MEOW_SHUFFLE_inv(xmm5, xmm6, xmm7, xmm1, xmm2, xmm3);
    MEOW_SHUFFLE_inv(xmm6, xmm7, xmm0, xmm2, xmm3, xmm4);
    MEOW_SHUFFLE_inv(xmm7, xmm0, xmm1, xmm3, xmm4, xmm5);
    MEOW_SHUFFLE_inv(xmm0, xmm1, xmm2, xmm4, xmm5, xmm6);
    MEOW_SHUFFLE_inv(xmm1, xmm2, xmm3, xmm5, xmm6, xmm7);
    MEOW_SHUFFLE_inv(xmm2, xmm3, xmm4, xmm6, xmm7, xmm0);
    MEOW_SHUFFLE_inv(xmm3, xmm4, xmm5, xmm7, xmm0, xmm1);
    MEOW_DUMP_STATE("PostMix_inv", xmm0, xmm1, xmm2, xmm3, xmm4, xmm5, xmm6, xmm7, 0);


    pxor_clear(xmm9, xmm9);
    pxor_clear(xmm11, xmm11);
    uint8_t* Last = (uint8_t*)Message + (Len & ~0xf);
    int unsigned Len8 = (Len & 0xf);
    if (Len8)
    {
        xmm8 = _mm_loadu_si128((__m128i*)(&MeowMaskLen[0x10 - Len8]));
        uint8_t* LastOk = (uint8_t*)((((uint32_t)(((uint8_t*)Message) + Len - 1)) | (Block_Size - 1)) - 16);
        int Align = (Last > LastOk) ? ((int)(uint32_t)Last) & 0xf : 0;
        xmm10 = _mm_loadu_si128((__m128i*)(&MeowShiftAdjust[Align]));
        xmm9 = _mm_loadu_si128((__m128i*)(Last - Align));
        pshufb(xmm9, xmm10);
        pand(xmm9, xmm8);
    }
    if (Len & 0x10)
    {
        xmm11 = xmm9;
        xmm9 = _mm_loadu_si128((__m128i*)(Last - 0x10));
    }
    xmm8 = xmm9;
    xmm10 = xmm9;
    palignr(xmm8, xmm11, 15);
    palignr(xmm10, xmm11, 1);
    pxor_clear(xmm12, xmm12);
    pxor_clear(xmm13, xmm13);
    pxor_clear(xmm14, xmm14);
    movq(xmm15, Len);
    palignr(xmm12, xmm15, 15);
    palignr(xmm14, xmm15, 1);
    MEOW_DUMP_STATE("Residuals_inv", xmm8, xmm9, xmm10, xmm11, xmm12, xmm13, xmm14, xmm15, 0);


    int unsigned LaneCount = (Len >> 5) & 0x7;
    if (LaneCount == 0) goto MixDown; MEOW_MIX_inv(xmm2, xmm6, xmm0, xmm3, xmm4, rax + 0x00); --LaneCount;
    if (LaneCount == 0) goto MixDown; MEOW_MIX_inv(xmm3, xmm7, xmm1, xmm4, xmm5, rax + 0x20); --LaneCount;
    if (LaneCount == 0) goto MixDown; MEOW_MIX_inv(xmm4, xmm0, xmm2, xmm5, xmm6, rax + 0x40); --LaneCount;
    if (LaneCount == 0) goto MixDown; MEOW_MIX_inv(xmm5, xmm1, xmm3, xmm6, xmm7, rax + 0x60); --LaneCount;
    if (LaneCount == 0) goto MixDown; MEOW_MIX_inv(xmm6, xmm2, xmm4, xmm7, xmm0, rax + 0x80); --LaneCount;
    if (LaneCount == 0) goto MixDown; MEOW_MIX_inv(xmm7, xmm3, xmm5, xmm0, xmm1, rax + 0xa0); --LaneCount;
    if (LaneCount == 0) goto MixDown; MEOW_MIX_inv(xmm0, xmm4, xmm6, xmm1, xmm2, rax + 0xc0); --LaneCount;

MixDown:
    MEOW_DUMP_STATE("PostLanes", xmm0, xmm1, xmm2, xmm3, xmm4, xmm5, xmm6, xmm7, 0);


    MEOW_MIX_REG_inv(xmm1, xmm5, xmm7, xmm2, xmm3, xmm12, xmm13, xmm14, xmm15);
    MEOW_MIX_REG_inv(xmm0, xmm4, xmm6, xmm1, xmm2, xmm8, xmm9, xmm10, xmm11);
    MEOW_DUMP_STATE("PostAppend_inv", xmm0, xmm1, xmm2, xmm3, xmm4, xmm5, xmm6, xmm7, 0);


    uint32_t BlockCount = (Len >> 8);
    if (BlockCount > 0x3ff)
    {
        while (BlockCount--)
        {
            _mm_prefetch((char*)(rax + Block_Size + 0x00), _MM_HINT_T0);
            _mm_prefetch((char*)(rax + Block_Size + 0x40), _MM_HINT_T0);
            _mm_prefetch((char*)(rax + Block_Size + 0x80), _MM_HINT_T0);
            _mm_prefetch((char*)(rax + Block_Size + 0xc0), _MM_HINT_T0);

            MEOW_MIX_inv(xmm0, xmm4, xmm6, xmm1, xmm2, rax + 0x00);
            MEOW_MIX_inv(xmm1, xmm5, xmm7, xmm2, xmm3, rax + 0x20);
            MEOW_MIX_inv(xmm2, xmm6, xmm0, xmm3, xmm4, rax + 0x40);
            MEOW_MIX_inv(xmm3, xmm7, xmm1, xmm4, xmm5, rax + 0x60);
            MEOW_MIX_inv(xmm4, xmm0, xmm2, xmm5, xmm6, rax + 0x80);
            MEOW_MIX_inv(xmm5, xmm1, xmm3, xmm6, xmm7, rax + 0xa0);
            MEOW_MIX_inv(xmm6, xmm2, xmm4, xmm7, xmm0, rax + 0xc0);
            MEOW_MIX_inv(xmm7, xmm3, xmm5, xmm0, xmm1, rax + 0xe0);

            rax += 0x100;
        }
    }
    else
    {
        while (BlockCount--)
        {
            MEOW_MIX_inv(xmm0, xmm4, xmm6, xmm1, xmm2, rax + 0x00);
            MEOW_MIX_inv(xmm1, xmm5, xmm7, xmm2, xmm3, rax + 0x20);
            MEOW_MIX_inv(xmm2, xmm6, xmm0, xmm3, xmm4, rax + 0x40);
            MEOW_MIX_inv(xmm3, xmm7, xmm1, xmm4, xmm5, rax + 0x60);
            MEOW_MIX_inv(xmm4, xmm0, xmm2, xmm5, xmm6, rax + 0x80);
            MEOW_MIX_inv(xmm5, xmm1, xmm3, xmm6, xmm7, rax + 0xa0);
            MEOW_MIX_inv(xmm6, xmm2, xmm4, xmm7, xmm0, rax + 0xc0);
            MEOW_MIX_inv(xmm7, xmm3, xmm5, xmm0, xmm1, rax + 0xe0);

            rax += 0x100;
        }
    }

    MEOW_DUMP_STATE("PostBlocks_inv", xmm0, xmm1, xmm2, xmm3, xmm4, xmm5, xmm6, xmm7, 0);

    Print_Res(xmm0); Print_Res(xmm1); Print_Res(xmm2); Print_Res(xmm3);
    Print_Res(xmm4); Print_Res(xmm5); Print_Res(xmm6); Print_Res(xmm7);
}
```
### 主函数调用
导入上述所实现的头文件后，将哈希值定义为sdu_cst_20220610，将姓名学号作为消息信息转入MeowHash_inv函数中。注意这里需要先转换为十六进制后再做传参。
```c
#include <stdio.h>
#include<iostream>
#include"hash_find.h"
using namespace std;

int main()
{
    char Hash[] = "sdu_cst_20220610";
    cout << "Hash value:" << Hash << endl;
    char name_student_ID[] = "Wei Zhaolin 202000460083";
    cout <<endl<< "name_student_ID:" <<endl<< name_student_ID << endl;

    char hash_ascii[50] = "";
    for (int i = 0; i < 16; i++) 
        hash_ascii[i] = (int)Hash[i];
    cout << endl << "find key result:" << endl;
    MeowHash_inv(hash_ascii, strlen(name_student_ID), name_student_ID);
    return 0;
}
```
## 打印结果展示
![图片](https://user-images.githubusercontent.com/105708747/182007815-5c09fad8-68a2-4ef5-97be-830286ab76e0.png)
## 参考内容
[1]https://github.com/cmuratori
