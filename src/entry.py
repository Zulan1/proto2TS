from doctest import Example
import string
import utils
import random


class Entry:
  optional: bool
  repeated: bool
  type: string
  typePackage: string
  name: string
  enum: bool
  interface: bool
  oneOf: list
  
  def __init__(self):
    self.optional = False
    self.repeated = False
    self.type = ''
    self.typePackage = ''
    self.name = ''
    self.enum = False
    self.interface = False
    self.oneOf = []

  def buildEntry(self, entryString, basicTypes, enums ,imports):
    entryString = ' '.join(list(word for word in entryString.split(' ') if word.strip() != ''))
    entryString = self.setOptional(entryString, imports)
    entryString = self.setRepeated(entryString, imports)
    entryString = self.setType(entryString, basicTypes)
    self.setEnumAndInterface(enums, basicTypes, imports)
    self.setName(entryString)

  def setOptional(self, entryString: str, imports):
    if entryString.strip().startswith('optional '):
      self.optional = True
      entryString = ' '.join(entryString.strip().split(' ')[1:])
      imports['class-validator']['IsOptional'] = True
    elif not entryString.strip().startswith('repeated '):
      imports['class-validator']['IsNotEmpty'] = True

    return entryString

  def setRepeated(self, entryString: str, imports):
    if entryString.strip().startswith('repeated '):
      self.repeated = True
      entryString = ' '.join(entryString.strip().split(' ')[1:])
      imports['class-validator']['IsOptional'] = True
      imports['class-validator']['IsArray'] = True
    return entryString

  def setType(self, entryString: str, basicTypes: dict):
    self.type = entryString.strip().split(' ')[0]
    if '.' in self.type:
      self.typePackage = self.type.split('.')[0].strip()
      self.type = self.type.split('.')[1].strip()
    return ' '.join(entryString.strip().split(' ')[1:])

  def setName(self, entryString: str):
    self.name = entryString.split('=')[0].strip()

  def setEnumAndInterface(self, enums, basicTypes: dict, imports: dict):
    if self.type in enums:
      self.enum = True
      imports['class-validator']['IsEnum'] = True
      imports['interfaces'].add(f'Enums/{self.type}')
      return
    if self.type in basicTypes.keys():
      return
    self.interface = True
    imports['class-validator']['ValidateNested'] = True
    imports['class-transformer']['Type'] = True
    imports['interfaces'].add(f'{self.typePackage}/{self.type}')
  
  def buildOneOf(self, oneOfBlock: str, basicTypes, enums, imports):
    openingBracket = oneOfBlock.find('{')
    closingBracket = openingBracket + utils.findClosingBracket(oneOfBlock[openingBracket:])
    startLineIndex = oneOfBlock.find('\n', openingBracket) + 1
    self.name = oneOfBlock.split('oneof')[1].split('{')[0].strip()
    for line in oneOfBlock[startLineIndex:closingBracket - 1].split('\n'):
      if line.strip() == '': continue
      entry = Entry()
      entry.buildEntry('optional ' + line, basicTypes, enums, imports)
      self.oneOf.append(entry)
    return self, closingBracket + 2
  
  def toString(self, basicTypes: dict, imports: dict, swagger: bool, enums: list):
    entryString = ''
    if self.oneOf == []:
      if self.optional or self.repeated:
        entryString += '  @IsOptional()\n'
        if self.repeated:
          entryString += '  @IsArray()\n'
      else:
        entryString += '  @IsNotEmpty()\n'
      if self.interface:
        if self.repeated:
          entryString += '  @ValidateNested({ each: true })\n'
        else:
          entryString += '  @ValidateNested()\n'
        entryString += f'  @Type(() => {self.type})\n'
      elif self.enum:
        if self.repeated:
          entryString += f'  @IsEnum({self.type}' + ', { each: true })\n'
        else: 
          entryString += f'  @IsEnum({self.type})\n'
      else:
        validation = basicTypes[self.type]['validation']
        imports['class-validator'][validation] = True
        if self.repeated:
          entryString += f'  @{validation}''({}, { each: true })\n'
        else:
          entryString += f'  @{validation}()\n'
      if swagger:
        imports['@nestjs/swagger']['ApiProperty'] = True
        entryString += '  @ApiProperty({\n  '
        if self.enum:
          entryString += f'enum: {self.type},\n  '
          exampleValue = f'Object.values({self.type})[Math.floor(Math.random() * Object.values({self.type}).length)]'
          if self.repeated: # deal with enum array
            exampleValue = f'[{exampleValue}]'
            entryString += 'isArray: true,\n  '
          entryString += f'example: {exampleValue},\n  '
        if self.optional or self.repeated:
          entryString += 'required: false,\n  '
        else:
          entryString += 'required: true,\n  '
        if self.repeated:
          if self.type in basicTypes.keys():
            entryString += 'type:' + f' [{basicTypes[self.type]["jsType"]}],\n  ' + f'example: {basicTypes[self.type]["example"](self.repeated)},\n  '
          elif self.type not in enums:
            entryString += 'type:' + f' [{self.type}],\n  '
        else:
          if self.type in basicTypes.keys():
            entryString += 'type:' + f' {basicTypes[self.type]["jsType"]},\n  ' + f'example: {basicTypes[self.type]["example"](self.repeated)},\n  '
          elif self.type not in enums:
            entryString += 'type:' + f' {self.type},\n  '
        entryString += '})\n'
      if self.optional or self.repeated:
        entryString += f'  {self.name}?: '
      else:
        entryString += f'  {self.name}: '
      if self.repeated:
        if self.type in basicTypes.keys():
          entryString += f'{basicTypes[self.type]["tsType"]}[];\n'
        else:
          entryString += f'{self.type}[];\n'
      else:
        if self.type in basicTypes.keys():
          entryString += f'{basicTypes[self.type]["tsType"]};\n'
        else:
          entryString += f'{self.type};\n'
    else:
      entryString = '\n'.join(one.toString(basicTypes, imports , swagger, enums) for one in self.oneOf)
      entryString += '\n  @IsNotEmpty()\n'
      entryString += '  @IsIn([' + ', '.join(list(f'\'{one.name}\'' for one in self.oneOf)) + '])\n'
      imports['class-validator']['IsIn'] = True
      if swagger:
        entryString += '  @ApiProperty({\n  required: true,\n    type: String,\n    example: ' f'\'{self.oneOf[random.randint(0, len(self.oneOf) - 1)].name}\',' '\n  })\n'
      entryString += f'  {self.name}:\n    | ' + '\n    | '.join(f'\'{one.name}\'' for one in self.oneOf) + ';\n'
    return entryString

        


  