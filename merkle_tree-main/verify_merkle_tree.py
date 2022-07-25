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