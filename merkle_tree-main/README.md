# merkle_tree
使用list变量存储整颗merkle tree，开始时的输入即为最底部的叶子结点，随后逐步向上推进。list中的最后一个元素即为根节点root。其中添加了verify功能，可以验证局部merkletree的正确性，也可以验证整颗merkletree的正确性。  
本次实验通过调用hashlib库使用sha256函数对叶子结点进行哈希。在主函数中，test即为所有的叶子结点，通过调用所写函数构造merkle tree，若最终验证通过则说明正确性。下面将对具体函数进行介绍。
```python
import hashlib
from cap_root import cap_root
from set_merkle_tree import set_merkle_tree
from verify_merkle_tree import set_proof_2_verify, verify


def sha256(value):
  md5 = hashlib.md5()
  md5.update(value.encode(encoding='utf-8'))
  return md5.hexdigest()


def main():
  test = ['aa', 'bb', 'cc', 'dd', 'ee', 'ff']
  tree = set_merkle_tree(test, sha256)
  root = cap_root(test, sha256)
  proof = set_proof_2_verify(tree, test[2])
  print("proof for verify is:",proof)
  result = verify(proof, sha256)
  print("verify results:",result)
  print("merkle tree is:",tree)
  print("merkle tree's root is:",root)

if __name__ == '__main__':
  main()
```
首先，编写一个cap_root函数使得其能够快速找到根节点所对应的hash值，函数输入为一个列表以及一个函数func，在具体使用时，该列表arr即为文件的具体分组即叶子结点，而func即为sha256。首先获取列表长度进行循环，每次循环中以步长为2进行遍历，若为偶数那么则左右两两分组，若为奇数那么剩余左右相等。将左右结点相加结果通过func函数即sha256进行哈希，并将其逐层向上传递，最终便能得到一颗完整的merkle tree，最终返回final_root的第一个元素即为根节点。代码如下：
```python
def cap_root(arr, func):
  """arr is an arr,func is a function"""
  final_root = []
  final_root.extend(arr)
  length = len(arr)
  while length > 1:
    temp = 0
    for i in range(0, length, 2):
      left = final_root[i]
      if(i + 1 == length):
        right = left
      else:
        right = final_root[i+1]
      final_root[temp] = func(left+right)
      temp += 1
    length = temp
  return final_root[0]
```
其次，编写能够找到计算左右孩子的根节点函数，方法同上因此不再赘述，代码如下：
```python
def cal_upper_node(arr, func):
  """arr is an arr,func is a function"""
  upper_node = []
  length = len(arr)
  for i in range(0, length, 2):
    left = arr[i]
    if (i + 1 == length):
      right = left
    else:
      right = arr[i + 1]
    upper_node.append(func(left+right))

  return upper_node
```
利用上述函数构造merkle tree，输入为列表以及一个func，具体使用时仍是所有叶子结点以及sha256。通过将叶子结点两两分组，将左右孩子相加后经过sha256哈希加入到final_tree中，最终返回整棵树即可。代码如下：
```python
def set_merkle_tree (arr, func):
  """arr is an arr,func is a function"""
  if len(arr) == 1:
    return arr

  temp_arr = arr
  final_tree = []
  final_tree.extend(arr)
  while len(temp_arr) > 1:
    temp_arr = cal_upper_node(temp_arr, func)
    final_tree.extend(temp_arr)

  return final_tree
```
最终编写函数对构造的merkle tree进行验证，代码如下：
```python
def cal_width (a, b):
  """calculate the width of the tree"""
  return (a + (1 << b) - 1) >> b

def count_treenode (leaf_num):
  """count the number of the treenode"""
  nums = 1
  temp = leaf_num
  while temp > 1:
    nums += temp
    temp = (temp + 1) >> 1
  return nums


def set_proof_2_verify (arr, data):
  """set up proof for verify"""
  length = len(arr)
  index = arr.index(data)
  res = []
  width = cal_width(length, 1)
  while width > 0:
    if count_treenode(width) == length:
      break
    width -= 1

  temp_index = 0
  height = 0
  while temp_index < length -1:
    width2 = cal_width(width, height)
    height += 1
    ji_ou = index % 2
    if ji_ou != 0:
      index -= 1

    index2 = temp_index + index
    left = arr[index2]
    if(index == width2 - 1):
      right = left
    else:
      right = arr[index2 + 1]

    if temp_index > 0:
      if ji_ou != 0:
        res.append(left)
        res.append(None)
      else:
        res.append(None)
        res.append(right)
    else:
      res.append(left)
      res.append(right)

    index = int(index/2) | 0
    temp_index += width2
  res.append(arr[length - 1])
  return res


def verify(arr, func):
  """arr is an arr,func is a function,verify merkle tree is right"""
  if arr == None:
    return False
  root = arr[len(arr) - 1]
  hash_val = root
  for i in range(0, len(arr) - 1, 2):
    left = arr[i] or hash_val
    right = arr[i + 1] or hash_val
    hash_val = func(left + right)
  if(hash_val == root):
    return True
  else:
    return False
```
