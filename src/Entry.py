# Zifan Yang
# zyang45@jhu.edu
import random
import collections

Std_Int_Size = 4

class Entry():
    startPos = -1
    endPos = -1
    def toString(self):
        pass


class Constant(Entry):
    typePtr = None
    val = None
    Id = -1
    size = Std_Int_Size
    def __init__(self, typePtr, val, startPos=-1, endPos=-1):
        self.typePtr = typePtr
        self.val = val
        self.startPos = startPos
        self.endPos = endPos
        self.Id = random.randint(0, 100000)

    def toString(self):
        debugMsg = blue(" Constant ")
        typeInfo = ""
        valInfo = ""
        if self.typePtr is not None:
            typeInfo = self.typePtr.toString()
        if self.val is not None:
            valInfo = str(self.val)
        return debugMsg + typeInfo + " | " + valInfo + " " + str(self.Id)

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_Constant(self, idx)
        else:
            visitor.Graph_Visit_Constant(self, idx)

    def buildENV(self, MyInterpreterVisitor):
        return MyInterpreterVisitor.Visit_Constant(self)

    def allocStorage(self, MyCodeGenVisitor, curAddr):
        return MyCodeGenVisitor.Visit_Constant(self, curAddr)


class Variable(Entry):
    typePtr = None
    Id = -1
    addr = 0
    def __init__(self, typePtr, startPos=-1, endPos=-1):
        self.typePtr = typePtr
        self.startPos = startPos
        self.endPos = endPos
        self.Id = random.randint(0, 100000)

    def setAddr(self, addr):
        self.addr = addr

    def getAddr(self):
        return self.addr

    def toString(self):
        debugMsg = blue(" Variable ")
        typeInfo = ""
        if self.typePtr is not None:
            typeInfo = self.typePtr.toString()
        return debugMsg + typeInfo + str(self.Id)

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_Variable(self, idx)
        else:
            visitor.Graph_Visit_Variable(self, idx)

    def buildENV(self, MyInterpreterVisitor):
        return MyInterpreterVisitor.Visit_Variable(self)

    def allocStorage(self, MyCodeGenVisitor, curAddr):
        return MyCodeGenVisitor.Visit_Variable(self, curAddr)


class Type(Entry):
    def toString(self):
        pass


class Integer(Type):
    size = Std_Int_Size

    def calcSize(self):
        self.size = Std_Int_Size

    def toString(self):
        debugMsg =blue(" Integer ")
        return debugMsg

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_Integer(self, idx)
        else:
            visitor.Graph_Visit_Integer(self, idx)

    def buildENV(self, MyInterpreterVisitor):
        return MyInterpreterVisitor.Visit_Integer(self)

    def allocStorage(self, MyCodeGenVisitor, curAddr):
        return MyCodeGenVisitor.Visit_Integer(self, curAddr)



class Array(Type):
    typePtr = None
    length = None
    Id = -1
    size = 0
    def __init__(self, typePtr, length, startPos=-1, endPos=-1):
        self.typePtr = typePtr
        self.length = length
        self.startPos = startPos
        self.endPos = endPos
        self.Id = random.randint(0, 100000)
        self.calcSize()

    def calcSize(self):
        self.size = self.typePtr.size * self.length.val

    def toString(self):
        debugMsg = blue(" Array ")
        typeInfo = ""
        lengthInfo = ""
        if self.typePtr is not None:
            typeInfo = self.typePtr.toString()
        if self.length is not None:
            lengthInfo = self.length.toString()
        return debugMsg + typeInfo + " | " + lengthInfo + str(self.Id)

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_Array(self, idx)
        else:
            visitor.Graph_Visit_Array(self, idx)

    def buildENV(self, MyInterpreterVisitor):
        return MyInterpreterVisitor.Visit_Array(self)

    def allocStorage(self, MyCodeGenVisitor, curAddr):
        return MyCodeGenVisitor.Visit_Array(self, curAddr)


class Record(Type):
    scopePtr = None
    Id = -1
    size = 0
    def __init__(self, scopePtr, startPos=-1, endPos=-1):
        self.scopePtr = scopePtr
        self.startPos = startPos
        self.endPos = endPos
        self.Id = random.randint(0, 100000)
        self.calcSize()

    def calcSize(self):
        self.size = self.scopePtr.size

    def toString(self):
        debugMsg = blue(" Record ")
        scopePtrInfo = ""
        if self.scopePtr is not None:
            scopePtrInfo = self.scopePtr.toString()
        return debugMsg + scopePtrInfo + str(self.Id)

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_Record(self, idx)
        else:
            visitor.Graph_Visit_Record(self, idx)

    def buildENV(self, MyInterpreterVisitor):
        return MyInterpreterVisitor.Visit_Record(self)

    def allocStorage(self, MyCodeGenVisitor, curAddr):
        return MyCodeGenVisitor.Visit_Record(self, curAddr)


class Field(Entry):
    typePtr = None
    Id = -1
    addr = 0
    def __init__(self, typePtr, startPos=-1, endPos=-1):
        self.typePtr = typePtr
        self.startPos = startPos
        self.endPos = endPos
        self.Id = random.randint(0, 100000)

    def setAddr(self, addr):
        self.addr = addr

    def getAddr(self):
        return self.addr

    def toString(self):
        debugMsg = blue(" Field ")
        typeInfo = ""
        if self.typePtr is not None:
            typeInfo = self.typePtr.toString()
        return debugMsg + typeInfo + str(self.Id)

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_Field(self, idx)
        else:
            visitor.Graph_Visit_Field(self, idx)

    def buildENV(self, MyInterpreterVisitor):
        return MyInterpreterVisitor.Visit_Field(self)

    def allocStorage(self, MyCodeGenVisitor, curAddr):
        return MyCodeGenVisitor.Visit_Field(self, curAddr)


class Scope():
    LocalDict = {}
    outerScope = None
    Id = -1
    size = 0
    def __init__(self, outerScope = None):
        self.LocalDict = {}
        self.outerScope = outerScope
        self.Id = random.randint(0, 100000)

    def insert(self, name, value):
        self.LocalDict[name] = value
        self.LocalDict = collections.OrderedDict(sorted(self.LocalDict.items()))

        self.updateSize(value)

    def updateSize(self, value):
        if isinstance(value, Integer) or isinstance(value, Array) or isinstance(value, Record):
            value.calcSize()
            self.size += value.size
        elif isinstance(value, Variable) or isinstance(value, Field):
            self.size += value.typePtr.size
        elif isinstance(value, Constant):
            self.size += value.size

    def find(self, name):
        tmpScope = self
        while tmpScope is not None:
            if tmpScope.LocalDict.has_key(name) is True:
                return tmpScope.LocalDict[name]
            tmpScope = tmpScope.outerScope
        return None

    def local(self, name):
        return self.LocalDict.has_key(name)

    def toString(self):
        debugMsg = red(" Scope ")
        keyList = ""
        if self.LocalDict is not None:
            keyList = self.LocalDict.keys()
        return debugMsg + str(keyList) + str(self.Id)

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_Scope(self, idx)
        else:
            visitor.Graph_Visit_Scope(self, idx)

    def buildENV(self, MyInterpreterVisitor, isProgramScope=False):
        if isProgramScope is False:
            return MyInterpreterVisitor.Visit_Scope(self)
        else:
            return MyInterpreterVisitor.Visit_PROGRAM_Scope(self)

    def allocStorage(self, MyCodeGenVisitor, curAddr, isProgramScope=False):
        if isProgramScope is False:
            return MyCodeGenVisitor.Visit_Scope(self, curAddr)
        else:
            return MyCodeGenVisitor.Visit_PROGRAM_Scope(self, curAddr)



def green(text):
    # return "\033[1;32m{}\033[0;0m".format(text)
    return text

def red(text):
    # return "\033[1;31m{}\033[0;0m".format(text)
    return text

def blue(text):
    # return "\033[1;34m{}\033[0;0m".format(text)
    return text


# We should only have one Integer object
singleton_Integer = Integer()

# Unit Test for Entry.py
if __name__ == "__main__":
    print(red("--------- Entry.py Unit Test --------\n"))
    myConstant = Constant(singleton_Integer, 10)
    print(myConstant.toString())
    print("Constant Construction .................. "+green("Succeed"))

    myVariable = Variable(singleton_Integer)
    print(myVariable.toString())
    print("Variable Construction .................. "+green("Succeed"))

    print(singleton_Integer.toString())
    print("Integer Construction .................. "+green("Succeed"))

    myArray = Array(singleton_Integer, myConstant)
    print(myArray.toString())
    print("Array Construction .................. "+green("Succeed"))

    Global_Scope = Scope()
    Global_Scope.insert("A", Field(singleton_Integer))
    Global_Scope.insert("B", Field(singleton_Integer))
    Global_Scope.insert("C", Field(singleton_Integer))
    Global_Scope.insert("D", Field(Array(singleton_Integer, myConstant)))
    print(Global_Scope.find("B").toString())
    assert Global_Scope.find("E") == None
    assert Global_Scope.local("A") == True
    assert Global_Scope.local("E") == False
    print(Global_Scope.toString())
    print("Scope Construction .................. "+green("Succeed"))

    innerScope = Scope(Global_Scope)
    innerScope.insert("a", Constant(singleton_Integer, 1))
    innerScope.insert("b", Constant(singleton_Integer, 2))
    innerScope.insert("c", Variable(singleton_Integer))
    innerScope.insert("d", Array(singleton_Integer, myConstant))
    print(innerScope.find("B").toString())
    assert innerScope.find("E") == None
    assert innerScope.find("a") != None
    assert innerScope.find("A") != None
    assert innerScope.local("A") == False
    assert innerScope.local("E") == False
    assert innerScope.local("a") == True
    print("Nested Scope Construction .................. "+green("Succeed"))
    
    myRecord = Record(innerScope)
    print(myRecord.toString())
    print("Record Construction .................. "+green("Succeed"))
