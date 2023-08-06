def findClosingBracket(block):
  count = 1
  forPos = block.find('{')
  backPos = block.find('}')
  forPos = block.find('{', forPos + 1)
  if forPos == -1:
    return backPos
  while count > 0:
    if forPos < backPos and forPos != -1:
      forPos = block.find('{', forPos + 1)
      count += 1
    elif backPos < forPos or forPos == -1:
      if count == 1:
        return backPos
      backPos = block.find('}', backPos + 1)
      count -=1
  return backPos


def findPackageName(fullBlock):
  return fullBlock.split('package ')[1].split(';')[0].strip()


def removeBlock(block, index):
  openingBracket = block.find('{', index + 1)
  closingBracket = openingBracket + findClosingBracket(block[openingBracket:])
  block = block[:index] + block[closingBracket + 1:]
  return block