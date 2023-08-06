import os
import utils


enums = set()
packageName = ''


def createEnum(enumBlock, dst):
  global packageName, enums
  enumName = enumBlock.split('enum ')[1].split('{')[0].strip()
  enums.add(enumName)
  if not os.path.exists(f'./generated/Enums'):
    os.mkdir(f'{dst}/Enums')
  openIndex = enumBlock.find('{')
  if enumBlock[openIndex - 1] != ' ':
    if enumBlock[openIndex - 1] == '\n':
      enumBlock = enumBlock.replace('\n', ' ', 1)
    else:
      enumBlock = enumBlock[:openIndex] + ' ' + enumBlock[openIndex:]
      openIndex += 1
  enumBlock = enumBlock.replace(';', ',')
  enumBlock = enumBlock.replace('    }', '}')
  enumBlock = enumBlock.replace('  }', '}')
  enumBlock = enumBlock.replace('    }', '}')
  enumBlock = enumBlock.replace('\n        ', '\n  ')
  enumBlock = enumBlock.replace('\n    ', '\n  ')
  enumValues = enumBlock.split('\n')
  enumValues = list(filter(lambda s: s.strip() != '', enumValues)) # get rid of comments and empty lines
  for index in range(1, len(enumValues) - 1): # go over only the value strings
    str = enumValues[index]
    key = str.split('=')[0].strip()
    equalIndex = str.index('=')
    str = str[:equalIndex + 1] + '\'' + key + '\','
    enumValues[index] = str
  enumBlock = '\n'.join(enumValues)
  with open(f'{dst}/Enums/{enumName}.enum.ts', 'w') as f:
    f.write('export ' + enumBlock.strip() + '\n')


def createEnums(source, dst):
  global packageName, enums
  for file in os.listdir(source):
    if os.path.isdir(f'./{source}/{file}'):
      createEnums(f'{source}/{file}', dst)
    if file.split('.')[-1] != 'proto': continue
    with open(os.path.join(source, file), 'r') as f:
      data = f.read()
      data = '\n'.join(list(d.split('//')[0] for d in data.split('\n')))
    packageName = utils.findPackageName(data[::-1][::-1])
    index = data.find('enum ')
    while index != -1:
      indexEnd = index + utils.findClosingBracket(data[index:])
      createEnum(data[index:indexEnd + 1][::-1][::-1], dst)
      index = data.find('enum ', index + 1)
  return enums
