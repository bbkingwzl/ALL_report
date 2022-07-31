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