import random
import string


def intExample(isArray):
  if isArray:
    length = random.randint(1, 10)
    return list(intExample(False) for _ in range(length))
  return random.randint(-10000, 10000)

def uintExample(isArray):
  if isArray:
    length = random.randint(1, 10)
    return list(uintExample(False) for _ in range(length))
  return random.randint(0, 10000)

def floatExample(isArray):
  if isArray:
    length = random.randint(1, 10)
    return list(floatExample(False) for _ in range(length))
  return f'{(random.random() - 0.5) * 179:.4f}'

def stringExample(isArray):
  if isArray:
    length = random.randint(1, 10)
    return list(stringExample(False) for _ in range(length))
  length = 10
  letters = string.ascii_letters
  result_str = ''.join(random.choice(letters) for i in range(length))
  return f'\'{result_str}\'' # -> `$\'{result}\'`

def boolExample(isArray):
  if isArray:
    length = random.randint(1, 10)
    return list(boolExample(False) for _ in range(length))
  choice = random.random()
  if choice < 0.5:
    return 'false'
  return 'true'

def basicTypes():
  return {
    'int32': { 'tsType': 'number', 'jsType': 'Number', 'example': intExample, 'validation': 'IsNumber' },
    'int64': { 'tsType': 'number', 'jsType': 'Number', 'example': intExample, 'validation': 'IsNumber' },
    'uint32': { 'tsType': 'number', 'jsType': 'Number', 'example': uintExample, 'validation': 'IsNumber' },
    'uint64': { 'tsType': 'number', 'jsType': 'Number', 'example': uintExample, 'validation': 'IsNumber' },
    'sint32': { 'tsType': 'number', 'jsType': 'Number', 'example': intExample, 'validation': 'IsNumber' },
    'sint64': { 'tsType': 'number', 'jsType': 'Number', 'example': intExample, 'validation': 'IsNumber' },
    'fixed32': { 'tsType': 'number', 'jsType': 'Number', 'example': intExample, 'validation': 'IsNumber' },
    'fixed64': { 'tsType': 'number', 'jsType': 'Number', 'example': intExample, 'validation': 'IsNumber' },
    'sfixed32': { 'tsType': 'number', 'jsType': 'Number', 'example': intExample, 'validation': 'IsNumber' },
    'sfixed64': { 'tsType': 'number', 'jsType': 'Number', 'example': intExample, 'validation': 'IsNumber' },
    'float': { 'tsType': 'number', 'jsType': 'Number', 'example': floatExample, 'validation': 'IsNumber' },
    'double': { 'tsType': 'number', 'jsType': 'Number', 'example': floatExample, 'validation': 'IsNumber' },
    'string': { 'tsType': 'string', 'jsType': 'String', 'example': stringExample, 'validation': 'IsString' },
    'bytes': { 'tsType': 'string', 'jsType': 'String', 'example': stringExample, 'validation': 'IsString' },
    'bool': { 'tsType': 'boolean', 'jsType': 'Boolean', 'example': boolExample, 'validation': 'IsBoolean' },



  }
