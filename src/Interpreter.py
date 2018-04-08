# Zifan Yang
# zyang45@jhu.edu
import Box
import Entry
from Stack import *
import sys
from Global import GlobalVal

class Interpreter():
    myErrHandler = None
    Program_Scope = None
    AST_root = None
    def __init__(self, Program_Scope, AST_root, myErrHandler):
        self.Program_Scope = Program_Scope
        self.AST_root = AST_root
        self.myErrHandler = myErrHandler

    def interpret(self):
        MyInterpreterVisitor_ST = InterpreterVisitor_ST(self.myErrHandler)
        if self.Program_Scope is not None:
            self.Program_Scope.buildENV(MyInterpreterVisitor_ST, isProgramScope=True)

        MyInterpreterVisitor_AST = InterpreterVisitor_AST(MyInterpreterVisitor_ST.ENV, self.myErrHandler)
        if self.AST_root is not None:
            self.AST_root.accept_Interpreter(MyInterpreterVisitor_AST)

        # for key in MyInterpreterVisitor_ST.ENV:
        #     print("  "+str(key)+" "+str(MyInterpreterVisitor_ST.ENV[key]))




class InterpreterVisitor_ST():
    ENV = {}
    myErrHandler = None
    def __init__(self, myErrHandler):
        self.ENV = {}
        self.myErrHandler = myErrHandler

    """
    Build box and Environment
    """
    def Visit_PROGRAM_Scope(self, curScope):
        for key in curScope.LocalDict:
            if isinstance(curScope.LocalDict.get(key), Entry.Variable):
                storage = curScope.LocalDict.get(key).buildENV(self)
                self.ENV[key] = storage

    def Visit_Scope(self, curScope):
        scopeDict = {}
        for key in curScope.LocalDict:
            if isinstance(curScope.LocalDict.get(key), Entry.Field):
                curBox = curScope.LocalDict.get(key).buildENV(self)
                scopeDict[key] = curBox
        return scopeDict

    def Visit_Field(self, curField):
        curBox = curField.typePtr.buildENV(self)
        return curBox

    def Visit_Record(self, curRecord):
        inputDict = curRecord.scopePtr.buildENV(self)
        curBox = Box.RecordBox(inputDict, curRecord.startPos, curRecord.endPos, self.myErrHandler)
        return curBox

    def Visit_Array(self, curArray):
        length = curArray.length.val
        elemBox = curArray.typePtr.buildENV(self)
        inputList = []
        for i in range(0, length):
            inputList.append(elemBox.makeCopy())

        curBox = Box.ArrayBox(inputList, curArray.startPos, curArray.endPos, self.myErrHandler)
        return curBox

    def Visit_Integer(self, curInteger):
        curBox = Box.IntegerBox(0, curInteger.startPos, curInteger.endPos, self.myErrHandler)
        return curBox

    def Visit_Variable(self, curVariable):
        curBox = curVariable.typePtr.buildENV(self)
        return curBox

    def Visit_Constant(self, curConstant):
        # curConstant.typePtr.buildENV(self)
        return None



class InterpreterVisitor_AST():
    ENV = {}
    myErrHandler = None
    sk = None

    def __init__(self, ENV, myErrHandler):
        self.ENV = ENV
        self.myErrHandler = myErrHandler
        self.sk = Stack()

    def getExpressionFromTop(self, startPos, endPos):
        header = "Error @("+str(startPos)+" "+str(endPos)+") "
        if self.sk.isEmpty() is True:
            errMsg = header + "When Interpreting AST Expression, stack is empty"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, startPos)
            return None
        if isinstance(self.sk.peek(), int) is True:
            return self.sk.pop()
        elif isinstance(self.sk.peek(), Box.IntegerBox) is True:
            curBox = self.sk.pop()
            return curBox.value
        else:
            errMsg = header + "When Interpreting AST Expression, Expectiong a IntegerBox or Integer on stack top"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, startPos)
            return None

    def Interpreter_Visit_Variable(self, astVariable):
        varName = astVariable.Id
        if self.ENV.has_key(varName) is True:
            curBox = self.ENV[varName]
            self.sk.push(curBox)
        else:
            header = "Error @("+str(astVariable.startPos)+" "+str(astVariable.endPos)+") "
            errMsg = header + "When Interpreting AST Variable Node, No box is found"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astVariable.startPos)


    def Interpreter_Visit_Index(self, astIndex):
        header = "Error @("+str(astIndex.startPos)+" "+str(astIndex.endPos)+") "
        astIndex.location.accept_Interpreter(self)
        astIndex.expression.accept_Interpreter(self)

        exp = self.getExpressionFromTop(astIndex.startPos, astIndex.endPos)

        if self.sk.isEmpty() is True:
            errMsg = header + "When Interpreting AST Index => location, stack is empty"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astIndex.startPos)
        loc = self.sk.pop()
        if isinstance(loc, Box.ArrayBox) is False:
            errMsg = header + "When Interpreting AST Index => location, Expectiong a ArrayBox on Top"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astIndex.startPos)
        else:
            newBox = loc.getArrayElement(exp, astIndex.startPos, astIndex.endPos)
            self.sk.push(newBox)


    def Interpreter_Visit_Field(self, astField):
        header = "Error @("+str(astField.startPos)+" "+str(astField.endPos)+") "
        astField.location.accept_Interpreter(self)
        # astField.variable.accept_Interpreter(self)

        var = astField.variable.Id

        if self.sk.isEmpty() is True:
            errMsg = header + "When Interpreting AST Field => location, stack is empty"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astField.startPos)
        loc = self.sk.pop()
        if isinstance(loc, Box.RecordBox) is False:
            errMsg = header + "When Interpreting AST Field => location, Expectiong a RecordBox on Top"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astField.startPos)
        else:
            newBox = loc.getRecordField(var, astField.startPos, astField.endPos)
            self.sk.push(newBox)


    def Interpreter_Visit_Number(self, astNumber):
        curNum = astNumber.val
        self.sk.push(curNum)


    def Interpreter_Visit_Binary(self, astBinary):
        header = "Error @("+str(astBinary.startPos)+" "+str(astBinary.endPos)+") "
        astBinary.left.accept_Interpreter(self)
        astBinary.right.accept_Interpreter(self)

        right = self.getExpressionFromTop(astBinary.startPos, astBinary.endPos)
        left = self.getExpressionFromTop(astBinary.startPos, astBinary.endPos)

        if str(astBinary.op) == "+":
            self.sk.push(left+right)
        elif str(astBinary.op) == "-":
            self.sk.push(left-right)
        elif str(astBinary.op) == "*":
            self.sk.push(left*right)
        elif str(astBinary.op) == "DIV":
            if right == 0:
                errMsg = header + "When Interpreting AST Binary => op, cannot DIV 0"
                self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astBinary.startPos)
            else:
                self.sk.push(left/right)
        elif str(astBinary.op) == "MOD":
            if right == 0:
                errMsg = header + "When Interpreting AST Binary => op, cannot MOD 0"
                self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astBinary.startPos)
            else:
                self.sk.push(left%right)
        else:
            errMsg = header + "When Interpreting AST Binary => op, found unknown op"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astBinary.startPos)


    def Interpreter_Visit_Condition(self, astCondition):
        header = "Error @("+str(astCondition.startPos)+" "+str(astCondition.endPos)+") "
        astCondition.left.accept_Interpreter(self)
        astCondition.right.accept_Interpreter(self)

        right = self.getExpressionFromTop(astCondition.startPos, astCondition.endPos)
        left = self.getExpressionFromTop(astCondition.startPos, astCondition.endPos)

        res = 0
        if str(astCondition.op) == ">":
            if left > right:
                res = 1
            self.sk.push(res)
        elif str(astCondition.op) == "<":
            if left < right:
                res = 1
            self.sk.push(res)
        elif str(astCondition.op) == "=":
            if left == right:
                res = 1
            self.sk.push(res)
        elif str(astCondition.op) == "#":
            if left != right:
                res = 1
            self.sk.push(res)
        elif str(astCondition.op) == "<=":
            if left <= right:
                res = 1
            self.sk.push(res)
        elif str(astCondition.op) == ">=":
            if left >= right:
                res = 1
            self.sk.push(res)
        else:
            errMsg = header + "When Interpreting AST Condition => op, found unknown op"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astCondition.startPos)



    def Interpreter_Visit_Assign(self, astAssign):
        header = "Error @("+str(astAssign.startPos)+" "+str(astAssign.endPos)+") "
        astAssign.location.accept_Interpreter(self)
        astAssign.expression.accept_Interpreter(self)

        if self.sk.isEmpty() is True:
            errMsg = header + "When Interpreting AST Assign => expression, stack is empty"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astAssign.startPos)
        exp = self.sk.pop()

        if self.sk.isEmpty() is True:
            errMsg = header + "When Interpreting AST Assign => location, stack is empty"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astAssign.startPos)
        loc = self.sk.pop()
        if isinstance(loc, Box.Box) is False:
            errMsg = header + "When Interpreting AST Index => location, Expectiong a Box on Top"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astAssign.startPos)
        else:
            if isinstance(exp, int) is True:
                if isinstance(loc, Box.IntegerBox) is True:
                    loc.set(exp)
                else:
                    errMsg = header + "When Interpreting AST Assign => location, right side is a int and Expectiong left side be a IntegerBox"
                    self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astAssign.startPos)
            else:  # loc is a Box
                # loc = exp.makeCopy()
                exp.deepCopyBox(loc, astAssign.startPos, astAssign.endPos)

        self.sanityCheck(astAssign.startPos, astAssign.endPos, "ASSIGN")

        if astAssign.nextInst is not None:
            astAssign.nextInst.accept_Interpreter(self)


    def Interpreter_Visit_Read(self, astRead):
        header = "Error @("+str(astRead.startPos)+" "+str(astRead.endPos)+") "
        astRead.location.accept_Interpreter(self)

        if self.sk.isEmpty() is True:
            errMsg = header + "When Interpreting AST Read => location, stack is empty"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astRead.startPos)
        loc = self.sk.pop()
        if isinstance(loc, Box.IntegerBox) is False:
            errMsg = header + "When Interpreting AST Read => location, Expectiong a IntegerBox on Top"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astRead.startPos)
        else:
            isValid, resNum = self.getInputFromKeyboard()
            if isValid is True:
                loc.set(resNum)
            else:
                errMsg = header + "When Interpreting AST Read => location, Please input a valid INTEGER"
                self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astRead.startPos)

        self.sanityCheck(astRead.startPos, astRead.endPos, "READ")

        if astRead.nextInst is not None:
            astRead.nextInst.accept_Interpreter(self)


    def Interpreter_Visit_Write(self, astWrite):
        astWrite.expression.accept_Interpreter(self)

        exp = self.getExpressionFromTop(astWrite.startPos, astWrite.endPos)
        print(exp)

        self.sanityCheck(astWrite.startPos, astWrite.endPos, "WRITE")

        if astWrite.nextInst is not None:
            astWrite.nextInst.accept_Interpreter(self)


    def Interpreter_Visit_If(self, astIf):
        header = "Error @("+str(astIf.startPos)+" "+str(astIf.endPos)+") "
        astIf.cond.accept_Interpreter(self)

        if self.sk.isEmpty() is True:
            errMsg = header + "When Interpreting AST If => condition, stack is empty"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astIf.startPos)
        cond = self.sk.pop()
        if isinstance(cond, int) is False:
            errMsg = header + "When Interpreting AST If => condition, Expectiong a Integer on Top"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astIf.startPos)
        elif cond not in [0, 1]:
            errMsg = header + "When Interpreting AST If => condition, found a Integer on Top not 0 or 1"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astIf.startPos)

        if cond == 1:   #  True
            astIf.true_Inst.accept_Interpreter(self)
        else:
            if astIf.false_Inst is not None:
                astIf.false_Inst.accept_Interpreter(self)

        self.sanityCheck(astIf.startPos, astIf.endPos, "IF")

        if astIf.nextInst is not None:
            astIf.nextInst.accept_Interpreter(self)


    def Interpreter_Visit_Repeat(self, astRepeat):
        header = "Error @("+str(astRepeat.startPos)+" "+str(astRepeat.endPos)+") "
        cnt = 0
        while True:
            astRepeat.inst.accept_Interpreter(self)
            astRepeat.cond.accept_Interpreter(self)

            if self.sk.isEmpty() is True:
                errMsg = header + "When Interpreting AST Repeat => condition, stack is empty"
                self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astRepeat.startPos)
            cond = self.sk.pop()
            if isinstance(cond, int) is False:
                errMsg = header + "When Interpreting AST Repeat => condition, Expectiong a Integer on Top"
                self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astRepeat.startPos)
            elif cond not in [0, 1]:
                errMsg = header + "When Interpreting AST Repeat => condition, found a Integer on Top not 0 or 1"
                self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, astRepeat.startPos)
            if cond == 1:
                break

        self.sanityCheck(astRepeat.startPos, astRepeat.endPos, "REPEAT")

        if astRepeat.nextInst is not None:
            astRepeat.nextInst.accept_Interpreter(self)

    def getInputFromKeyboard(self):
        num = None
        isNeg = False
        rawStr = sys.stdin.readline().strip('\n').lstrip().rstrip()
        if len(rawStr) == 0:
            return False, 0
        if rawStr[0] == '-':
            isNeg = True
            rawStr = rawStr[1:]
        for i in range(0, len(rawStr)):
            if rawStr[i] not in GlobalVal.DIGIT:
                return False, 0
        resNum = int(rawStr)
        if isNeg == True:
            resNum = -resNum
        return True, resNum


    def sanityCheck(self, instructionName, startPos, endPos):
        header = "Error @("+str(startPos)+" "+str(endPos)+") "
        if self.sk.isEmpty() is False:
            errMsg = header + "When finish processing instruction <<"+instructionName+">>, the stack is not empty"
            self.myErrHandler.Record_Interpreter_Err("Interpreter", errMsg, startPos)


if __name__ == "__main__":
    TestInterpreterVisitor_AST = InterpreterVisitor_AST(None, None)
    while True:
        print(TestInterpreterVisitor_AST.getInputFromKeyboard())
        print("----------")
