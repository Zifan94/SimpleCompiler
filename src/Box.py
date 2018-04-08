# Zifan Yang
# zyang45@jhu.edu
import copy

class Box():
    startPos = -1
    endPos = -1
    myErrHandler = None

class IntegerBox(Box):
    value = 0

    def __init__(self, value, startPos, endPos, myErrHandler):
        self.value = value
        self.startPos = startPos
        self.endPos = endPos
        self.myErrHandler = myErrHandler

    def get(self):
        return self.value

    def set(self, value):
        self.value = value

    def makeCopy(self):
        newIntegerBox = IntegerBox(self.value, self.startPos, self.endPos, self.myErrHandler)
        return newIntegerBox

    def deepCopyBox(self, target, startPos, endPos):
        header = "Error @("+str(startPos)+" "+str(endPos)+") "
        if isinstance(target, IntegerBox) is False:
            errMsg = header + "When IntegerBox.deepCopyBox(), target is not a IntegerBox"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, self.startPos)
        target.startPos = self.startPos
        target.endPos = self.endPos
        target.value = self.value


class ArrayBox(Box):
    length = None
    boxes = None

    def __init__(self, inputList, startPos, endPos, myErrHandler):
        self.length = len(inputList)
        self.boxes = inputList
        self.startPos = startPos
        self.endPos = endPos
        self.myErrHandler = myErrHandler

    def getArrayElement(self, offset, startPos, endPos):
        if 0 <= offset and offset < self.length:
            return self.boxes[offset]
        else:
            header = "Error @("+str(startPos)+" "+str(endPos)+") "
            errMsg = header + "When getArrayElement(), ArrayBox index out of range"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, self.startPos)

    def makeCopy(self):
        newBoxes = []
        for i in range(0, self.length):
            newBoxes.append(self.boxes[i].makeCopy())
        newArrayBox = ArrayBox(newBoxes, self.startPos, self.endPos, self.myErrHandler)
        return newArrayBox

    def deepCopyBox(self, target, startPos, endPos):
        header = "Error @("+str(startPos)+" "+str(endPos)+") "
        if isinstance(target, ArrayBox) is False:
            errMsg = header + "When ArrayBox.deepCopyBox(), target is not a ArrayBox"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, self.startPos)
        target.startPos = self.startPos
        target.endPos = self.endPos
        target.length = self.length
        target.boxes = copy.deepcopy(self.boxes)


class RecordBox(Box):
    boxesDict = None

    def __init__(self, inputDict, startPos, endPos, myErrHandler):
        self.boxesDict = inputDict
        self.startPos = startPos
        self.endPos = endPos
        self.myErrHandler = myErrHandler

    def getRecordField(self, fieldName, startPos, endPos):
        if self.boxesDict.has_key(fieldName) is True:
            return self.boxesDict[fieldName]
        else:
            header = "Error @("+str(startPos)+" "+str(endPos)+") "
            errMsg = header + "When getRecordField(), Field Name "+str(fieldName)+" does not found"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, self.startPos)

    def makeCopy(self):
        newBoxesDict = {}
        for key in self.boxesDict:
            newBoxesDict[key] = self.boxesDict[key].makeCopy()
        newRecordBox = RecordBox(newBoxesDict, self.startPos, self.endPos, self.myErrHandler)
        return newRecordBox

    def deepCopyBox(self, target, startPos, endPos):
        header = "Error @("+str(startPos)+" "+str(endPos)+") "
        if isinstance(target, RecordBox) is False:
            errMsg = header + "When RecordBox.deepCopyBox(), target is not a RecordBox"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, self.startPos)
        target.startPos = self.startPos
        target.endPos = self.endPos
        target.boxesDict = copy.deepcopy(self.boxesDict)




