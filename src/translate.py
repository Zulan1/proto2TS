import os
import shutil
import enums
import utils
from entry import *
from basicTypes import *
from createExports import *


def translateEntry(entryString, block):
  global imports, swagger, bT, enumList
  if entryString.strip() == '}' or entryString.strip() == '':
    prevIndex = block.find(entryString)
    index = block.find('\n', prevIndex + 1)
    return '', index
  entry = Entry()
  if entryString.strip().startswith('oneof'):
    index = block.find(entryString)
    entryString, closingBracket = entry.buildOneOf(block[index:], bT, enumList, imports)
    return entry.toString(bT, imports, swagger, enumList), index + closingBracket
  entry.buildEntry(entryString, bT, enumList, imports)
  prevIndex = block.find(entryString)
  index = block.find(';', prevIndex)
  return entry.toString(bT, imports, swagger, enumList), index + 1
    


def writeImports():
  global imports, enumList
  importsString = ''
  for key in imports.keys():
    if key == 'interfaces': continue
    imported = list(imp for imp, flag in list(imports[key].items()) if flag)
    if imported:
      importsString += 'import { ' + ', '.join(imported) + ' } ' f'from \'{key}\';\n'
  for imp in imports['interfaces']:
    pacName = imp.split('/')[0].strip()
    imported = imp.split('/')[1].strip()
    type = 'enum' if imported in enumList else 'dto'
    if pacName:
      importsString += 'import { ' f'{imported}' ' }' f' from \'../{pacName}/{imported}.{type}\';\n'
    else:
      importsString += 'import { ' f'{imported}' ' }' f' from \'./{imported}.{type}\';\n'

  importsString += '\n\n'
  return importsString


def translateBlock(block):
  global packageName, imports, swagger, dst
  imports = {
  'class-validator': {'IsNotEmpty': False, 'IsOptional': False, 'IsNumber': False, 'IsString': False, 'IsBoolean': False, 'IsEnum': False, 'ValidateNested': False, 'IsIn': False, 'IsArray': False},
  'class-transformer': {'Type': False},
  '@nestjs/swagger': {'ApiProperty': False},
  'interfaces': set()
  }
  translatedEntries = []
  if not block.startswith('message '): return
  className = block.split('message ')[1].split('{')[0].strip()
  index = block.find('{')
  closingBracket = index + utils.findClosingBracket(block[index:])
  index = block.find('\n', index + 1) + 1
  while index != -1 and index < closingBracket:
    translatedEntry, index = translateEntry(block[index:], block)
    if translatedEntry != '':
      translatedEntries.append(translatedEntry)
    if index == 0:
      break

  if not os.path.exists(f'{dst}/{packageName}'):
    os.mkdir(f'{dst}/{packageName}')
  with open(f'{dst}/{packageName}/{className}.dto.ts', 'w') as f:
    f.write(writeImports())
    f.write(f'export class {className} ' '{\n' + '\n'.join(translatedEntries) + '}')


def split2(item, delim):
  lst = item.split(delim)
  l = []
  for entry in lst:
    if entry.strip() != '':
      l.append(entry.strip())
  return l


def translateService(block):
  global imports
  imports = {
  'interfaces': set()
  }
  if not block.startswith('service '): return
  methods = set()
  serviceName = block.split('service ')[1].split('{')[0].strip()
  index = block.find('{')
  closingBracket = index + utils.findClosingBracket(block[index:])
  index = block.find('\n', index + 1) + 1
  while index != -1 and index < closingBracket:
    method, index = translateMethod(block[index:], block)
    if method != '':
      methods.add(method)
    if index == 0:
      break
  importsString = 'import { Observable } from \'rxjs\';\n' + writeImports()
  serviceBlock = f'export interface {serviceName} ' + '{\n  ' + '\n  '.join(methods) + '\n}'
  if not os.path.exists('./generated/Services'):
    os.mkdir('./generated/Services')
  with open(f'./generated/Services/{serviceName}.service.ts', 'w') as f:
    f.write(importsString + serviceBlock) 


def translateMethod(entryString, block):
  global imports, bT, enumList
  if not entryString.strip().startswith('rpc '): return '', block.find('\n', block.find(entryString) + 1) + 1
  methodName = entryString.split('rpc ')[1].split('(')[0].strip()
  inputStart = entryString.find('(')
  inputEnd = entryString.find(')')
  input = entryString[inputStart + 1:inputEnd].strip()
  returns = entryString.find('returns')
  outputStart = entryString.find('(', returns)
  outputEnd = entryString.find(')', returns)
  output = entryString[outputStart + 1:outputEnd].strip()
  arr = [input, output]
  for i in range(len(arr)):
    type = arr[i]
    package = ''
    if '.' in type:
      package = type.split('.')[0].strip()
      type = type.split('.')[1].strip()
    if type in enumList:
      imports['interfaces'].add(f'Enums/{type}')
      continue
    if type in bT.keys():
      continue
    imports['interfaces'].add(f'{package}/{type}')
    arr[i] = type
  input, output = arr
  prevIndex = block.find(entryString)
  index = block.find(';', prevIndex)
  return f'{methodName}(request: {input}): Observable<{output}>;', index + 1




def translateProtoFile(data):
  global packageName
  packageName = data.split('package ')[1].split(';')[0].strip()
  index = data.find('\n')
  while index != -1:
    if data[index:].strip().startswith('message '):
      index = data.find('message ', index)
      closingBracket = index + utils.findClosingBracket(data[index:])
      translateBlock(data[index:closingBracket + 1].strip())
      index = closingBracket
    elif data[index:].strip().startswith('service '):
      index = data.find('service ', index)
      closingBracket = index + utils.findClosingBracket(data[index:])
      translateService(data[index:closingBracket + 1].strip())
      index = closingBracket
    index = data.find('\n', index + 1)


def removeEnums(data):
  index = data.find('enum ')
  while index != -1:
    closingBracket = index + utils.findClosingBracket(data[index:])
    data = data[:index] + data[closingBracket + 1:]
    index = data.find('enum ', index + 1)
  return data


source = './protoFiles'
dst = './generated'
packageName = ''
if os.path.exists(dst):
  shutil.rmtree(dst)
os.mkdir(dst)
imports = dict()
swagger = os.getenv('SWAGGER', True) 
enumList = enums.createEnums(source, dst)
bT = basicTypes()
def main(source):
  for file in os.listdir(source):
    if os.path.isdir(f'./{source}/{file}'):
      main(f'{source}/{file}')
    if file.split('.')[-1] != 'proto': continue
    with open(os.path.join(source, file), 'r') as f:
      data = f.read()
      data = '\n'.join(list(d.split('//')[0] for d in data.split('\n'))).strip()
      while '/*' in data:
        start = data.find('/*')
        end = data.find('*/')
        data = data[:start] + data[end + 2:]
    data = removeEnums(data)
    translateProtoFile(data)

main(source)
createIndex()
  
