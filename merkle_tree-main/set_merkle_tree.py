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

