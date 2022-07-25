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