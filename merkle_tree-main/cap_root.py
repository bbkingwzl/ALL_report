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


