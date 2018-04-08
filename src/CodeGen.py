# Zifan Yang
# zyang45@jhu.edu
import Box
import Entry
from Stack import *
import sys
from Global import GlobalVal

class CodeGen():
    myErrHandler = None
    Program_Scope = None
    AST_root = None
    def __init__(self, Program_Scope, AST_root, myErrHandler):
        self.Program_Scope = Program_Scope
        self.AST_root = AST_root
        self.myErrHandler = myErrHandler

    def generateCode(self, filename = None):
        StorageAllocationCode = ""
        MyCodeGenVisitor_ST = CodeGenVisitor_ST(self.myErrHandler)
        if self.Program_Scope is not None:
            self.Program_Scope.allocStorage(MyCodeGenVisitor_ST, 0, isProgramScope=True)
            StorageAllocationCode = MyCodeGenVisitor_ST.show_Storage_Allocation_Code()

        totalStorage = MyCodeGenVisitor_ST.totalSize

        ARM_Code = ""
        MyCodeGenVisitor_AST = CodeGenVisitor_AST(self.myErrHandler)
        if self.AST_root is not None:
            self.AST_root.accept_CodeGen(MyCodeGenVisitor_AST)
            ARM_Code = MyCodeGenVisitor_AST.show_ARM_code(totalStorage)
        else:
            ARM_Code = MyCodeGenVisitor_AST.show_ARM_code(totalStorage)

        # check totalStorage Size as Machine Restriction
        errMsg = "When doing Storage Allocation, The amount of memory required to hold all Variables exceeding 42900000000!"
        if totalStorage >42900000000:
            self.myErrHandler.Record_Machine_Restriction_Err("Machine_Restriction", errMsg, -1)


        allCode = StorageAllocationCode + "\n\n@-------------------------\n\n" + ARM_Code
        
        outputFileName = "a.S"
        if filename is not None:
            if ".sim" in filename:
                outputFileName = filename[:-4]+".s"
            else:
                outputFileName = filename+".s"

            with open(outputFileName,'w') as f:
                    f.write(allCode)
        else:
            print(allCode+"\n")


class CodeGenVisitor_ST():
    space = "    "

    typeCode = {}
    varCode = {}
    fieldCode = {}
    totalSize = 0

    myErrHandler = None
    nextAddr = 0
    def __init__(self, myErrHandler):
        self.typeCode = {}
        self.varCode = {}
        self.fieldCode = {}
        self.myErrHandler = myErrHandler
        self.nextAddr = 0
        self.totalSize = 0

    """
    Build box and Environment
    """
    def Visit_PROGRAM_Scope(self, curScope, curAddr):
        for key in curScope.LocalDict:
            if isinstance(curScope.LocalDict.get(key), Entry.Variable):
                curVar = curScope.LocalDict.get(key)
                curVar.setAddr(curAddr)
                curVar.allocStorage(self, 0)
                curAddr += curVar.typePtr.size
                self.totalSize = curAddr
                self.varCode[self.space+str(key)+" Var_addr: "+str(curVar.getAddr())] = 1
            
            elif isinstance(curScope.LocalDict.get(key), Entry.Constant):
                curConst = curScope.LocalDict.get(key)
                curConst.allocStorage(self, 0)

    def Visit_Scope(self, curScope, curAddr):
        for key in curScope.LocalDict:
            if isinstance(curScope.LocalDict.get(key), Entry.Field):
                curField = curScope.LocalDict.get(key)
                curField.setAddr(curAddr)
                curField.allocStorage(self, 0)
                curAddr += curField.typePtr.size

                self.fieldCode[self.space+str(key)+" Fld_addr: "+str(curField.getAddr())] = 1

    def Visit_Field(self, curField, curAddr):
        # curField.setAddr(curAddr)
        curField.typePtr.allocStorage(self, 0)

    def Visit_Record(self, curRecord, curAddr):
        curRecord.scopePtr.allocStorage(self, 0)
        curRecord.calcSize()

        self.typeCode[self.space+(str(curRecord)+" RCD_size: "+str(curRecord.size))] = 1

    def Visit_Array(self, curArray, curAddr):
        curArray.typePtr.allocStorage(self, 0)
        curArray.calcSize()

        self.typeCode[self.space+(str(curArray)+" ARR_size: "+str(curArray.size))] = 1

    def Visit_Integer(self, curInteger, curAddr):
        curInteger.calcSize()

        self.typeCode[self.space+(str(curInteger)+" INT_size: "+str(curInteger.size))] = 1

    def Visit_Variable(self, curVariable, curAddr):
        # curVariable.setAddr(curAddr)
        curVariable.typePtr.allocStorage(self, 0)

    def Visit_Constant(self, curConstant, curAddr):
        self.checkConstantSize(curConstant.val, curConstant.startPos, curConstant.endPos)

    def show_Storage_Allocation_Code(self):
        typeOutput = "@ Type Storage Allocation:\n"
        for key in self.typeCode:
            typeOutput += "@ "+key+'\n'

        varOutput = "@ Varaiable Storage Allocation:\n"
        for key in self.varCode:
            varOutput += "@ "+key+'\n'

        fieldOutput = "@ Field Storage Allocation:\n"
        for key in self.fieldCode :
            fieldOutput += "@ "+key+'\n'
        outputCode = typeOutput + "\n" + varOutput + "\n" + fieldOutput
        return outputCode


    def checkConstantSize(self, num, curStartPos, curEndPos):
        errMsg = "Found "+str(num)+", while Declared constant must between -2^31 ~ 2^31-1, @("+str(curStartPos)+", "+str(curEndPos)+")"
        if num < -2147483648 or num > 2147483647:
            self.myErrHandler.Record_Machine_Restriction_Err("Machine_Restriction", errMsg, -1)























class CodeGenVisitor_AST():
    mainCode = ""
    codeDict = {}
    labelCode = ""
    dataCode = ""
    myErrHandler = None
    cond_label_exist = False
    sk = None
    labelCnt = 0
    loopCnt = 0
    assignCnt = 0
    labelSk = None
    sanityCheckErrorCnt = 0
    instructionCnt = 0
    LTORGCnt = 0

    def __init__(self, myErrHandler):
        self.mainCode = ""
        self.codeDict = {}
        self.labelCode = ""
        self.cond_label_exist = False
        self.dataCode = ""
        self.myErrHandler = myErrHandler
        self.sk = Stack()
        self.labelCnt = 0
        self.loopCnt = 0
        self.assignCnt = 0
        self.labelSk = Stack()
        self.labelSk.push("main")
        self.sanityCheckErrorCnt = 0
        self.instructionCnt = 0
        self.LTORGCnt = 0

        self.initDataCode()

    def addMainCode(self, curCode, labelName, isLabel = False):
        if self.codeDict.has_key(labelName) is False:
            self.codeDict[labelName] = ""
        if isLabel == False:
            self.codeDict[labelName] += "    "+curCode+"\n"
        else:
            self.codeDict[labelName] += curCode+"\n"


    def CodeGen_Visit_Variable(self, astVariable):
        curLabel = self.labelSk.peek()
        VarAddr = astVariable.ST.getAddr()
        VarSize = astVariable.ST.typePtr.size
        self.addMainCode("", curLabel)
        self.addMainCode("@ ## Visit Variable", curLabel)
        self.checkConstantSize(VarAddr, astVariable.startPos, astVariable.endPos)
        self.addMainCode("LDR R4, ="+str(VarAddr)+"        @ push Variable "+astVariable.Id, curLabel)

        self.addMainCode("PUSH {R4}"+"                  @ push Variable "+astVariable.Id, curLabel)

        self.sk.push("addr "+str(VarSize))
        self.process_literal_pool(2, curLabel)


    def CodeGen_Visit_Index(self, astIndex):
        curLabel = self.labelSk.peek()
        astIndex.location.accept_CodeGen(self)
        astIndex.expression.accept_CodeGen(self)

        elem_size = astIndex.location.curType.typePtr.size
        arrayLen = astIndex.location.curType.length.val
        startPos = astIndex.startPos
        endPos = astIndex.endPos

        self.addMainCode("", curLabel)
        self.addMainCode("@ ## Visit Index", curLabel)
        self.addMainCode("POP {R4}"+"                     @ Index: get Index.expression", curLabel)
        expType = self.sk.pop().split(" ")
        self.sk.pop()
        if expType[0] == 'addr':
            self.addMainCode("LDR R4, [R10, R4]"+"        @ Index: addr->num", curLabel)

        self.addMainCode("@     Checking array index out of bound", curLabel)
        self.addMainCode("LDR R6, ="+str(endPos)+"         @ Index: Error position", curLabel)
        self.checkConstantSize(endPos, astIndex.startPos, astIndex.endPos)
        self.addMainCode("LDR R7, ="+str(startPos)+"         @ Index: Error position", curLabel)
        self.checkConstantSize(startPos, astIndex.startPos, astIndex.endPos)
        self.addMainCode("PUSH {R6}"+"         @ Index: Error position", curLabel)
        self.addMainCode("PUSH {R7}"+"         @ Index: Error position", curLabel)
        self.addMainCode("CMP R4, #0"+"                  @ Index: check index >= 0", curLabel)
        self.addMainCode("BLLT Label_index_out_of_bound_err"+"                  @ Index: jump if index out of bound", curLabel)
        self.addMainCode("LDR R6, ="+str(arrayLen)+"     @ Index: array length in R6", curLabel)
        self.checkConstantSize(arrayLen, astIndex.startPos, astIndex.endPos)
        self.addMainCode("CMP R4, R6"+"     @ Index: check index >= 0", curLabel)
        self.addMainCode("BLGE Label_index_out_of_bound_err"+"                  @ Index: jump if index out of bound", curLabel)
        self.addMainCode("POP {R7}", curLabel)
        self.addMainCode("POP {R6}", curLabel)
        self.addMainCode("@     Finish Checking array index out of bound", curLabel)

        self.addMainCode("POP {R5}"+"                     @ Index: get Index.location", curLabel)
        self.addMainCode("LDR R7, ="+str(elem_size)+"     @ Index: get Index.location", curLabel)
        self.addMainCode("MUL R4, R4, R7"+"               @ Index: calc Index offset", curLabel)
        self.addMainCode("ADD R5, R4, R5"+"               @ Index: add offset with Index location", curLabel)

        self.addMainCode("PUSH {R5}"+"                    @ Index: push result Index", curLabel)
        self.sk.push("addr "+str(elem_size))

        self.addMainCode("", curLabel)
        self.process_literal_pool(18, curLabel)



    def CodeGen_Visit_Field(self, astField):
        curLabel = self.labelSk.peek()
        astField.location.accept_CodeGen(self)
        self.sk.pop()

        fieldOffset = astField.variable.ST.getAddr()
        fieldSize = astField.variable.ST.typePtr.size
        self.addMainCode("", curLabel)
        self.addMainCode("@ ## Visit Field", curLabel)
        self.addMainCode("POP {R4}"+"                        @ Field: get Field.location", curLabel)
        self.addMainCode("LDR R5, ="+str(fieldOffset)+"  @ Field: put field offset in R5", curLabel)
        self.checkConstantSize(fieldOffset, astField.startPos, astField.endPos)
        self.addMainCode("ADD R4, R4, R5"+"  @ Field: add with offset", curLabel)

        self.addMainCode("PUSH {R4}"+"                       @ Field: push result Field", curLabel)
        self.sk.push("addr "+str(fieldSize))

        self.addMainCode("", curLabel)
        self.process_literal_pool(4, curLabel)




    def CodeGen_Visit_Number(self, astNumber):
        curLabel = self.labelSk.peek()
        curNum = astNumber.val
        self.addMainCode("@ ## Visit Number", curLabel)
        self.addMainCode("LDR R4, ="+str(curNum)+"        @ push Number "+str(curNum), curLabel)
        self.checkConstantSize(curNum, astNumber.startPos, astNumber.endPos)
        self.addMainCode("PUSH {R4}"+"        @ push Number "+str(curNum), curLabel)
        self.sk.push("num")
        self.process_literal_pool(2, curLabel)


    def CodeGen_Visit_Binary(self, astBinary):
        curLabel = self.labelSk.peek()
        astBinary.left.accept_CodeGen(self)
        astBinary.right.accept_CodeGen(self)

        startPos = astBinary.startPos
        endPos = astBinary.endPos

        BinaryInstCnt = 0

        self.addMainCode("", curLabel)
        self.addMainCode("@ ## Visit Binary", curLabel)
        self.addMainCode("POP {R4}"+"        @ Binary: get Binary.right", curLabel)
        BinaryInstCnt = 1
        expType = self.sk.pop().split(" ")
        if expType[0] == 'addr':
            self.addMainCode("LDR R4, [R10, R4]"+"        @ Binary: addr->num", curLabel)
            BinaryInstCnt += 1
        self.addMainCode("POP {R5}"+"        @ Binary: get Binary.left", curLabel)
        BinaryInstCnt += 1
        expType = self.sk.pop().split(" ")
        if expType[0] == 'addr':
            self.addMainCode("LDR R5, [R10, R5]"+"        @ Binary: addr->num", curLabel)
            BinaryInstCnt += 1

        if str(astBinary.op) == "+":
            self.addMainCode("ADD R4, R5, R4"+"        @ Binary: perform +", curLabel)
            BinaryInstCnt += 1
        elif str(astBinary.op) == "-":
            self.addMainCode("SUB R4, R5, R4"+"        @ Binary: perform -", curLabel)
            BinaryInstCnt += 1
        elif str(astBinary.op) == "*":
            self.addMainCode("MUL R4, R5, R4"+"        @ Binary: perform *", curLabel)
            BinaryInstCnt += 1
        elif str(astBinary.op) == "DIV":
            self.addMainCode("@    Checking DIV 0 or not", curLabel)
            self.addMainCode("LDR R6, ="+str(endPos)+"         @ Binary: Error position", curLabel)
            self.checkConstantSize(endPos, astBinary.startPos, astBinary.endPos)
            self.addMainCode("LDR R7, ="+str(startPos)+"         @ Binary: Error position", curLabel)
            self.checkConstantSize(startPos, astBinary.startPos, astBinary.endPos)
            self.addMainCode("PUSH {R6}"+"         @ Binary: Error position", curLabel)
            self.addMainCode("PUSH {R7}"+"         @ Binary: Error position", curLabel)
            self.addMainCode("CMP R4, #0"+"                  @ Binary: check DIV 0", curLabel)
            self.addMainCode("BLEQ Label_div_mod_zero_err"+"                  @ Binary: jump if DIV 0", curLabel)
            self.addMainCode("POP {R7}", curLabel)
            self.addMainCode("POP {R6}", curLabel)
            self.addMainCode("@     Finish Checking DIV 0 or not", curLabel)

            self.addMainCode("MOV R0, R5"+"          @ Binary: perform DIV", curLabel)
            self.addMainCode("MOV R1, R4"+"          @ Binary: perform DIV", curLabel)
            self.addMainCode("BL __aeabi_idivmod"+"  @ Binary: perform DIV", curLabel)
            self.addMainCode("MOV R4, R0"+"          @ Binary: perform DIV", curLabel)
            BinaryInstCnt += 12
        elif str(astBinary.op) == "MOD":
            self.addMainCode("@     Checking MOD 0 or not", curLabel)
            self.addMainCode("LDR R6, ="+str(endPos)+"         @ Binary: Error position", curLabel)
            self.checkConstantSize(endPos, astBinary.startPos, astBinary.endPos)
            self.addMainCode("LDR R7, ="+str(startPos)+"         @ Binary: Error position", curLabel)
            self.checkConstantSize(startPos, astBinary.startPos, astBinary.endPos)
            self.addMainCode("PUSH {R6}"+"         @ Binary: Error position", curLabel)
            self.addMainCode("PUSH {R7}"+"         @ Binary: Error position", curLabel)
            self.addMainCode("CMP R4, #0"+"                  @ Binary: check MOD 0", curLabel)
            self.addMainCode("BLEQ Label_div_mod_zero_err"+"                  @ Binary: jump if MOD 0", curLabel)
            self.addMainCode("POP {R7}", curLabel)
            self.addMainCode("POP {R6}", curLabel)
            self.addMainCode("@     Finish Checking MOD 0 or not", curLabel)

            self.addMainCode("MOV R0, R5"+"          @ Binary: perform MOD", curLabel)
            self.addMainCode("MOV R1, R4"+"          @ Binary: perform MOD", curLabel)
            self.addMainCode("BL __aeabi_idivmod"+"  @ Binary: perform MOD", curLabel)
            self.addMainCode("MOV R4, R1"+"          @ Binary: perform MOD", curLabel)
            BinaryInstCnt += 12

        self.addMainCode("PUSH {R4}"+"       @ Binary: push the result back onto stack", curLabel)
        BinaryInstCnt += 1
        self.sk.push("num")

        self.addMainCode("", curLabel)
        self.process_literal_pool(BinaryInstCnt, curLabel)
            



    def CodeGen_Visit_Condition(self, astCondition):
        curLabel = self.labelSk.peek()
        self.addConditionLabel()

        astCondition.left.accept_CodeGen(self)
        astCondition.right.accept_CodeGen(self)
        self.addMainCode("@ ## Visit Condition", curLabel)
        self.addMainCode("POP {R4}"+"         @ Condition: get Condition.right", curLabel)
        expType = self.sk.pop().split(" ")
        if expType[0] == 'addr':
            self.addMainCode("LDR R4, [R10, R4]"+"        @ Condition: addr->num", curLabel)
        
        self.addMainCode("POP {R5}"+"         @ Condition: get Condition.left", curLabel)
        expType = self.sk.pop().split(" ")
        if expType[0] == 'addr':
            self.addMainCode("LDR R5, [R10, R5]"+"        @ Condition: addr->num", curLabel)

        self.addMainCode("CMP R5, R4"+"       @ Condition: get Condition.left", curLabel)
        if str(astCondition.op) == "=":
            self.addMainCode("BLNE label_push_false"+"        @ Condition: =", curLabel)
            self.addMainCode("BLEQ label_push_true"+"         @ Condition: =", curLabel)
        elif str(astCondition.op) == "#":
            self.addMainCode("BLEQ label_push_false"+"        @ Condition: #", curLabel)
            self.addMainCode("BLNE label_push_true"+"         @ Condition: #", curLabel)
        elif str(astCondition.op) == ">":
            self.addMainCode("BLLE label_push_false"+"        @ Condition: >", curLabel)
            self.addMainCode("BLGT label_push_true"+"         @ Condition: >", curLabel)
        elif str(astCondition.op) == ">=":
            self.addMainCode("BLLT label_push_false"+"        @ Condition: >=", curLabel)
            self.addMainCode("BLGE label_push_true"+"         @ Condition: >=", curLabel)
        elif str(astCondition.op) == "<":
            self.addMainCode("BLGE label_push_false"+"        @ Condition: <", curLabel)
            self.addMainCode("BLLT label_push_true"+"         @ Condition: <", curLabel)
        elif str(astCondition.op) == "<=":
            self.addMainCode("BLGT label_push_false"+"        @ Condition: <=", curLabel)
            self.addMainCode("BLLE label_push_true"+"         @ Condition: <=", curLabel)

        self.process_literal_pool(7, curLabel)

    def CodeGen_Visit_Assign(self, astAssign):
        curLabel = self.labelSk.peek()
        astAssign.location.accept_CodeGen(self)
        astAssign.expression.accept_CodeGen(self)

        self.addMainCode("", curLabel)
        self.addMainCode("@ ####  ASSIGN INSTRUCTION  ####", curLabel)
        self.addMainCode("POP {R4}"+"         @ Assign: get Assign.expression", curLabel)
        expType = self.sk.pop().split(" ")
        self.sk.pop()
        if expType[0] == 'addr':
            self.addMainCode("        "+"         @ Assign: Var to Var", curLabel)
            self.addMainCode("POP {R5}"+"         @ Assign: get Assign.location (init)", curLabel)
            expSize = expType[1]
            self.addMainCode("        "+"         @ Assign: start assign with variable size: "+str(expSize), curLabel)
            curSize = int(expSize)
            assignLabel = "Assign_Label_"+str(self.assignCnt)
            self.assignCnt += 1

            self.addMainCode("LDR R8, ="+str(curSize)+" @ Assign: LOOP ASSIGN, here is the total copy size", curLabel)
            self.checkConstantSize(curSize, astAssign.startPos, astAssign.endPos)
            self.addMainCode("MOV R6, #4", curLabel)
            self.addMainCode(assignLabel+":", curLabel, isLabel=True)
            self.addMainCode("LDR R7, [R10, R4]", curLabel)
            self.addMainCode("STR R7, [R10, R5]", curLabel)
            self.addMainCode("ADD R4, R4, R6", curLabel)
            self.addMainCode("ADD R5, R5, R6", curLabel)
            self.addMainCode("SUB R8, R8, R6", curLabel)
            self.addMainCode("MOV R7, #0", curLabel)
            self.addMainCode("CMP R8, R7", curLabel)
            self.addMainCode("BLGT "+assignLabel, curLabel)

            # for i in range(0, itrCnt):
            #     self.addMainCode("MOV R7, #"+str(i*4), curLabel)
            #     self.addMainCode("ADD R4, R4, R7", curLabel)
            #     self.addMainCode("ADD R5, R5, R7", curLabel)
            #     self.addMainCode("LDR R6, [R10, R4]", curLabel)
            #     self.addMainCode("STR R6, [R10, R5]"+"        @ Assign: 4 byte per time", curLabel)
        elif expType[0] == 'num':
            self.addMainCode("        "+"         @ Assign: Num to Var", curLabel)
            self.addMainCode("POP {R5}"+"         @ Assign: get Assign.location", curLabel)
            self.addMainCode("STR R4, [R10, R5]"+"        @ Assign: Var := Num", curLabel)

        self.sanityCheck("Assign")
        self.addMainCode("", curLabel)
        if astAssign.nextInst is not None:
            astAssign.nextInst.accept_CodeGen(self)

            self.process_literal_pool(14, curLabel)



    def CodeGen_Visit_Read(self, astRead):
        curLabel = self.labelSk.peek()
        astRead.location.accept_CodeGen(self)
        self.addMainCode("", curLabel)
        self.addMainCode("@ ####  READ INSTRUCTION  ####", curLabel)
        self.addMainCode("POP {R4}"+"               @ Read: get Read.location", curLabel)
        self.sk.pop()

        startPos = astRead.startPos
        endPos = astRead.endPos

        self.addMainCode("LDR R0, =scanFMT"+"       @ Read: begin scan", curLabel)
        self.addMainCode("LDR R1, =inputNum"+"      @ Read: .", curLabel)
        self.addMainCode("BL scanf"+"               @ Read: .", curLabel)

        self.addMainCode("@     Checking if user input is Int", curLabel)
        self.addMainCode("LDR R6, ="+str(endPos)+"         @ Read: Error position", curLabel)
        self.checkConstantSize(endPos, astRead.startPos, astRead.endPos)
        self.addMainCode("LDR R7, ="+str(startPos)+"         @ Read: Error position", curLabel)
        self.checkConstantSize(startPos, astRead.startPos, astRead.endPos)
        self.addMainCode("PUSH {R6}"+"         @ Read: Error position", curLabel)
        self.addMainCode("PUSH {R7}"+"         @ Read: Error position", curLabel)
        self.addMainCode("CMP R0, #0"+"                  @ Read: check scanf's return value is 0", curLabel)
        self.addMainCode("BLEQ Label_invalid_input_err"+"                  @ Read: jump if is 0", curLabel)
        self.addMainCode("POP {R7}", curLabel)
        self.addMainCode("POP {R6}", curLabel)
        self.addMainCode("@     Finish Checking if user input is Int", curLabel)

        self.addMainCode("LDR R5, =inputNum"+"      @ Read: .", curLabel)
        self.addMainCode("LDR R5, [R5]"+"           @ Read: scan result in R5", curLabel)
        self.addMainCode("STR R5, [R10, R4]"+"           @ Read: put num into location", curLabel)

        self.sanityCheck("Read")
        self.addMainCode("", curLabel)
        if astRead.nextInst is not None:
            astRead.nextInst.accept_CodeGen(self)
            self.process_literal_pool(15, curLabel)



    def CodeGen_Visit_Write(self, astWrite):
        curLabel = self.labelSk.peek()
        astWrite.expression.accept_CodeGen(self)
        self.addMainCode("", curLabel)
        self.addMainCode("@ ####  WRITE INSTRUCTION  ####", curLabel)
        self.addMainCode("POP {R4}"+"               @ Write: get Write.expression", curLabel)
        expType = self.sk.pop().split(" ")
        if expType[0] == 'addr':
            self.addMainCode("LDR R4, [R10, R4]"+"  @ Write: addr->num", curLabel)
        self.addMainCode("LDR R0, =printFMT"+"           @ Write", curLabel)
        self.addMainCode("MOV R1, R4"+"             @ Write", curLabel)
        self.addMainCode("BL printf"+"              @ Write", curLabel)

        self.sanityCheck("Write")
        self.addMainCode("", curLabel)
        if astWrite.nextInst is not None:
            astWrite.nextInst.accept_CodeGen(self)
            self.process_literal_pool(5, curLabel)


    def CodeGen_Visit_If(self, astIf):
        curLabel = self.labelSk.peek()
        astIf.cond.accept_CodeGen(self)

        curTrueLabel = "Label_IF_True_"+str(self.labelCnt)
        curFalseLabel = "Label_IF_False_"+str(self.labelCnt)
        self.labelCnt += 1

        self.addMainCode("", curLabel)
        self.addMainCode("@ ####  IF INSTRUCTION  ####", curLabel)
        self.addMainCode("POP {R4}"+"                @ If: get condition bool into R4", curLabel)
        self.addMainCode("CMP R4, #1"+"            @ If: if R4 is true?", curLabel)
        self.addMainCode("PUSH {R4}"+"               @ If: push condition back into stack", curLabel)
        self.addMainCode("BLEQ "+curTrueLabel+"    @ If: jump to true branch", curLabel)
        self.addMainCode("POP {R4}"+"                @ If: get condition bool into R4", curLabel)
        self.addMainCode("CMP R4, #1"+"            @ If: if R4 is true?", curLabel)
        self.addMainCode("BLNE "+curFalseLabel+"   @ If: jump to false branch", curLabel)

        self.labelSk.push(curTrueLabel)
        self.addMainCode("PUSH {R14}       @ in branch, save return addr",curTrueLabel)
        astIf.true_Inst.accept_CodeGen(self)
        self.addMainCode("POP {R14}        @ branch end, pop return addr",curTrueLabel)
        self.addMainCode("MOV pc, R14      @ return t",curTrueLabel)
        self.labelSk.pop()

        self.labelSk.push(curFalseLabel)
        self.addMainCode("PUSH {R14}       @ in branch, save return addr",curFalseLabel)
        if astIf.false_Inst is not None: 
            astIf.false_Inst.accept_CodeGen(self)
        self.addMainCode("POP {R14}        @ branch end, pop return addr",curFalseLabel)
        self.addMainCode("MOV pc, R14       @ return f",curFalseLabel)
        self.labelSk.pop()

        self.sanityCheck("If")
        self.addMainCode("", curLabel)
        if astIf.nextInst is not None:
            astIf.nextInst.accept_CodeGen(self)
            self.process_literal_pool(7, curLabel)



    def CodeGen_Visit_Repeat(self, astRepeat):
        curLabel = self.labelSk.peek()
        self.addMainCode("", curLabel)
        self.addMainCode("@ ####  REPEAT INSTRUCTION  ####", curLabel)
        loopLabel = "Label_REPEAT_"+str(self.loopCnt)
        self.loopCnt += 1

        self.codeDict[curLabel] += loopLabel+": \n"

        astRepeat.inst.accept_CodeGen(self)
        astRepeat.cond.accept_CodeGen(self)

        self.addMainCode("POP {R4}"+"                @ Repeat: get condition bool into R4", curLabel)
        self.addMainCode("CMP R4, #1"+"            @ Repeat: if R4 is true?", curLabel)
        self.addMainCode("BNE "+loopLabel+"        @ Repeat: jump back to loop if R4 != 1", curLabel)

        self.sanityCheck("Repeat")
        self.addMainCode("", curLabel)
        if astRepeat.nextInst is not None:
            astRepeat.nextInst.accept_CodeGen(self)
            self.process_literal_pool(3, curLabel)


    def sanityCheck(self, instructionName):
        curLabel = self.labelSk.peek()
        if self.sk.isEmpty() is False:
            self.addMainCode("@ ####  SANITYCHECK !!! FAILED !!! at instruction: "+instructionName+"  ####", curLabel)
            self.sanityCheckErrorCnt += 1
        else:
            self.addMainCode("@ ####  SANITYCHECK SUCCEED at instruction: "+instructionName+"  ####", curLabel)


    def addConditionLabel(self):
        if self.cond_label_exist is False:
            self.labelCode += "\nlabel_push_false:\n"
            self.labelCode += "    "+"MOV R4, #0"+"\n"
            self.labelCode += "    "+"PUSH {R4}"+"\n"
            self.labelCode += "    "+"MOV PC, R14"+"\n"
            self.labelCode += "\n"
            self.labelCode += "label_push_true:\n"
            self.labelCode += "    "+"MOV R4, #1"+"\n"
            self.labelCode += "    "+"PUSH {R4}"+"\n"
            self.labelCode += "    "+"MOV PC, R14"+"\n"
            self.labelCode += "\n"
            self.cond_label_exist = True

    def addLabelCode(self, code):
        self.labelCode += code+"\n"

    def initDataCode(self):
        self.dataCode += "\n  .data\n"
        self.dataCode += "printFMT:\n"
        self.dataCode += "  .asciz \"%d\\n\"\n"
        self.dataCode += "\n"

        self.dataCode += "scanFMT:\n"
        self.dataCode += "  .asciz \"%d\"\n"
        self.dataCode += "\n"

        self.dataCode += "inputNum:\n"
        self.dataCode += "  .word 0\n"
        self.dataCode += "\n"

        self.dataCode += "indexOutOfBoundFMT:\n"
        self.dataCode += "  .asciz \"error: array index out of bound @(%d, %d) \\n\"\n"
        self.dataCode += "\n"

        self.dataCode += "divmodZeroFMT:\n"
        self.dataCode += "  .asciz \"error: cannot DIV or MOD 0 @(%d, %d) \\n\"\n"
        self.dataCode += "\n"

        self.dataCode += "invalidInputFMT:\n"
        self.dataCode += "  .asciz \"error: invalid input, you should only input an Integer @(%d, %d) \\n\"\n"
        self.dataCode += "\n"

        self.dataCode += "  .end\n"

    def genStorageCode(self, totalStorage):
        size = totalStorage/4
        storageCode = ""
        storageCode += "\n  @ Storage Allocation Here\n"
        storageCode += "    MOV R5, #0"+"      @ base offset in R5\n"
        storageCode += "    MOV R6, #4"+"\n"
        storageCode += "    LDR R7, ="+str(size)+"  @ base size in R7\n"
        storageCode += "    MOV R8, #1"+"\n"
        storageCode += "Storage_Allocation_Label:"+"\n"
        storageCode += "    MOV R4, #0"+"\n"
        storageCode += "    STR R4, [R10, R5]"+"\n"
        storageCode += "    ADD R5, R5, R6"+"  @ add 4 offset each time\n"
        storageCode += "    SUB R7, R7, R8"+"\n"
        storageCode += "    CMP R7, R4"+"\n"
        storageCode += "    BLGT Storage_Allocation_Label"+"\n"
        storageCode += "  @ Storage Allocation END\n\n"
        return storageCode

    def indexOutOfBound(self):
        indexOutOfBoundCode = "\n"
        indexOutOfBoundCode += "Label_index_out_of_bound_err:\n"
        indexOutOfBoundCode += "    LDR R0, =stderr\n"
        indexOutOfBoundCode += "    LDR R0, [R0]\n"
        indexOutOfBoundCode += "    LDR R1, =indexOutOfBoundFMT\n"
        indexOutOfBoundCode += "    POP {R2}    @ start pos in R2\n"
        indexOutOfBoundCode += "    POP {R3}    @ end   pos in R2\n"
        indexOutOfBoundCode += "    BL fprintf    @ end   pos in R2\n"
        indexOutOfBoundCode += "    MOV R0, #1    @ call exit(0)\n"
        indexOutOfBoundCode += "    BL exit       @ call exit(0)\n"
        indexOutOfBoundCode += "    POP {fp, pc}  @ MAIN END\n\n"
        return indexOutOfBoundCode

    def divmodZero(self):
        indexOutOfBoundCode = "\n"
        indexOutOfBoundCode += "Label_div_mod_zero_err:\n"
        indexOutOfBoundCode += "    LDR R0, =stderr\n"
        indexOutOfBoundCode += "    LDR R0, [R0]\n"
        indexOutOfBoundCode += "    LDR R1, =divmodZeroFMT\n"
        indexOutOfBoundCode += "    POP {R2}    @ start pos in R2\n"
        indexOutOfBoundCode += "    POP {R3}    @ end   pos in R2\n"
        indexOutOfBoundCode += "    BL fprintf    @ end   pos in R2\n"
        indexOutOfBoundCode += "    MOV R0, #1    @ call exit(0)\n"
        indexOutOfBoundCode += "    BL exit       @ call exit(0)\n"
        indexOutOfBoundCode += "    POP {fp, pc}  @ MAIN END\n\n"
        return indexOutOfBoundCode

    def invalidInput(self):
        indexOutOfBoundCode = "\n"
        indexOutOfBoundCode += "Label_invalid_input_err:\n"
        indexOutOfBoundCode += "    LDR R0, =stderr\n"
        indexOutOfBoundCode += "    LDR R0, [R0]\n"
        indexOutOfBoundCode += "    LDR R1, =invalidInputFMT\n"
        indexOutOfBoundCode += "    POP {R2}    @ start pos in R2\n"
        indexOutOfBoundCode += "    POP {R3}    @ end   pos in R2\n"
        indexOutOfBoundCode += "    BL fprintf    @ end   pos in R2\n"
        indexOutOfBoundCode += "    MOV R0, #1    @ call exit(0)\n"
        indexOutOfBoundCode += "    BL exit       @ call exit(0)\n"
        indexOutOfBoundCode += "    POP {fp, pc}  @ MAIN END\n\n"
        return indexOutOfBoundCode

    def show_ARM_code(self, totalStorage):
        armCode = "@ by Zifan Yang\n"
        armCode += "@ Sanity Check Error: "+str(self.sanityCheckErrorCnt)+"\n\n"
        armCode += "    .comm vars, "+str(totalStorage)+", 4\n"
        armCode += "    .text\n"
        armCode += "    .global main\n"

        armCode += "main:\n"
        armCode += "    PUSH {fp, lr}  @ MAIN BEGIN\n"
        armCode += "    LDR R10, =vars @ R10 has the inital addr of vars\n\n"

        # armCode += self.genStorageCode(totalStorage)
        if self.codeDict.has_key("main") is False:
            self.codeDict["main"] = ""
        armCode += self.codeDict["main"]
        armCode += "\n"
        armCode += "    MOV R0, #0    @ call exit(0)\n"
        armCode += "    BL exit       @ call exit(0)\n"
        armCode += "    POP {fp, pc}  @ MAIN END\n\n"

        for key in self.codeDict:
            if key is not "main":
                armCode += "\n"+key+":\n"
                armCode += self.codeDict[key]

        armCode += self.labelCode
        armCode += self.indexOutOfBound()
        armCode += self.divmodZero()
        armCode += self.invalidInput()

        armCode += self.dataCode

        return armCode

    def checkConstantSize(self, num, curStartPos, curEndPos):
        errMsg = "Found "+str(num)+", while Literal constant must between -2^31 ~ 2^31-1, @("+str(curStartPos)+", "+str(curEndPos)+")"
        if num < -2147483648 or num > 2147483647:
            self.myErrHandler.Record_Machine_Restriction_Err("Machine_Restriction", errMsg, -1)


    def process_literal_pool(self, cmdCnt, curLabel):
        self.instructionCnt += cmdCnt
        if self.instructionCnt > 150:
            self.instructionCnt = 0
            self.addMainCode("b After_LTORG_"+str(self.LTORGCnt)+"                       @ LTORG", curLabel)
            self.addMainCode(".ltorg", curLabel)
            self.addMainCode("After_LTORG_"+str(self.LTORGCnt)+":", curLabel, True)
            self.LTORGCnt += 1



