import os

def addPathToIndex(path: str, lst: list):
  for file in os.listdir(path):
    filePath = os.path.join(path, file)
    if os.path.isdir(filePath):
      addPathToIndex(filePath, lst)
    elif os.path.isfile(filePath):
      lst.append(filePath)


def createIndex():
  lst = []
  addPathToIndex('./generated', lst)
  with open('./index.ts', 'w') as f:
    for file in lst:
      f.write(f'export * from \'{file[:-3]}\';\n')
