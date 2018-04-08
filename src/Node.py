# Zifan Yang
# zyang45@jhu.edu
import Entry
import ErrorHandler

class Node():
    startPos = -1
    endPos = -1
    def toString(self):
        pass

class Expression(Node):
    startPos = -1
    endPos = -1
    def toString(self):
        pass

class fakeExpression(Node):
    startPos = -1
    endPos = -1
    curType = Entry.singleton_Integer
    def toString(self):
        return "this is an faked Expression Node"


class Location(Expression):
    startPos = -1
    endPos = -1
    def toString(self):
        pass

class Variable(Location):
    Id = None
    ST = None
    curType = None
    def __init__(self, ST, startPos, endPos, myErrHandler, Id=None):
        self.ST = ST
        self.startPos = startPos
        self.endPos = endPos
        self.Id = Id

        header = "<AST> when constructing [Variable] @("+str(self.startPos)+", "+str(self.endPos)+"), "
        errMsg = ""
        if self.ST is None:
            errMsg = header + "found its ST is None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif isinstance(self.ST, Entry.Variable) is False and isinstance(self.ST, Entry.Field) is False:
            errMsg = header + "found its ST is not a Entry.Variable or Entry.Fieldtype"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        else:
            self.curType = ST.typePtr

    def toString(self):
        posInfo = " Node.Variable @("+str(self.startPos)+", "+str(self.endPos)+")"
        return posInfo + validStr(self.ST) + validStr(self.curType)

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_AST_Variable(self, idx)
        else:
            visitor.Graph_Visit_AST_Variable(self, idx)

    def accept_Interpreter(self, visitor):
        visitor.Interpreter_Visit_Variable(self)

    def accept_CodeGen(self, visitor):
        visitor.CodeGen_Visit_Variable(self)


class Index(Location):
    location = None
    expression = None
    curType = None
    def __init__(self, location, expression, startPos, endPos, myErrHandler):
        self.location = location
        self.expression = expression
        self.startPos = startPos
        self.endPos = endPos

        header = "<AST> when constructing [Index] @("+str(self.startPos)+", "+str(self.endPos)+"), "
        errMsg = ""
        if self.location is None:
            errMsg = header + "found its location is None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif self.expression is None:
            errMsg = header + "found its expression is None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

        elif isinstance(self.location, Location) is False:  # Rule  No.14
            errMsg = header + "found its location is not a Node.Location type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif isinstance(self.location.curType, Entry.Array) is False:
            errMsg = header +"found its location.curType is not a Entry.Array"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

        elif isinstance(self.expression, Expression) is False:
            errMsg = header + "found its expression is not a Node.Expression type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif isinstance(self.expression.curType, Entry.Integer) is False:
            errMsg = header + "found its expression is not a Entry.Integer"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        else:
            self.curType = self.location.curType.typePtr

    def toString(self):
        posInfo = " Node.Index @("+str(self.startPos)+", "+str(self.endPos)+")"
        return posInfo + validStr(self.location) + validStr(self.expression) + validStr(self.curType)

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_AST_Index(self, idx)
        else:
            visitor.Graph_Visit_AST_Index(self, idx)

    def accept_Interpreter(self, visitor):
        visitor.Interpreter_Visit_Index(self)

    def accept_CodeGen(self, visitor):
        visitor.CodeGen_Visit_Index(self)


class Field(Location):
    location = None
    variable = None
    curType = None
    def __init__(self, location, variable, startPos, endPos, myErrHandler):
        self.location = location
        self.variable = variable
        self.startPos = startPos
        self.endPos = endPos

        header = "<AST> when constructing [Field] @("+str(self.startPos)+", "+str(self.endPos)+"), "
        errMsg = ""
        if self.location is None:
            errMsg = header + "found its location is None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif self.variable is None:
            errMsg = header + "found its variable is None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

        elif isinstance(self.location, Location) is False:  # Rule  No.15
            errMsg = header + "found its location is not a Node.Location type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif isinstance(self.location.curType, Entry.Record) is False:
            errMsg = header +"found its location.curType is not a Entry.Record"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

        elif isinstance(self.variable, Variable) is False:
            errMsg = header + "found its variable is not a Node.Variable type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif isinstance(self.variable.ST, Entry.Field) is False:
            errMsg = header + "found its variable is not a Entry.Field"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        else:
            self.curType = self.variable.curType

    def toString(self):
        posInfo = " Node.Field @("+str(self.startPos)+", "+str(self.endPos)+")"
        return posInfo + validStr(self.location) + validStr(self.variable) + validStr(self.curType)

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_AST_Field(self, idx)
        else:
            visitor.Graph_Visit_AST_Field(self, idx)

    def accept_Interpreter(self, visitor):
        visitor.Interpreter_Visit_Field(self)

    def accept_CodeGen(self, visitor):
        visitor.CodeGen_Visit_Field(self)


class Number(Expression):
    ST = None
    val = None
    curType = None
    def __init__(self, ST, val, startPos, endPos, myErrHandler):
        self.val = val
        self.ST = ST
        self.startPos = startPos
        self.endPos = endPos

        header = "<AST> when constructing [Number] @("+str(self.startPos)+", "+str(self.endPos)+"), "
        errMsg = ""
        if self.val is None and self.ST is None:
            errMsg = header + "val and ST are both None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif self.val is None:
            if isinstance(self.ST, Entry.Constant) is False:
                errMsg = header + "ST must be a Entry.Constant type"
                myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
            else:
                self.val = self.ST.val
                self.curType = self.ST.typePtr
        elif self.ST is None:
            newConstant = Entry.Constant(Entry.singleton_Integer, self.val)
            self.ST = newConstant
            self.curType = self.ST.typePtr

    def toString(self):
        posInfo = " Node.Number @("+str(self.startPos)+", "+str(self.endPos)+")"
        return posInfo + validStr(self.ST) + str(self.val) + validStr(self.curType)

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_AST_Number(self, idx)
        else:
            visitor.Graph_Visit_AST_Number(self, idx)

    def accept_Interpreter(self, visitor):
        visitor.Interpreter_Visit_Number(self)

    def accept_CodeGen(self, visitor):
        visitor.CodeGen_Visit_Number(self)
         

class Binary(Expression):
    op = None
    left = None
    right = None
    curType = None
    def __init__(self, op, left, right, startPos, endPos, myErrHandler):
        self.op = op
        self.left = left
        self.right = right
        self.startPos = startPos
        self.endPos = endPos

        header = "<AST> when constructing [Binary] @("+str(self.startPos)+", "+str(self.endPos)+"), "
        errMsg = ""
        if self.op is None or self.op not in ["+", "-", "*", "DIV", "MOD"]:
            errMsg = header + "op is None or unknown string"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif self.left is None or self.right is None:
            errMsg = header + "left or right is None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

        elif isinstance(self.left, Expression) is False:
            errMsg = header + "left should be a Node.Expression type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif isinstance(self.right, Expression) is False:
            errMsg = header + "right should be a Node.Expression type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

        elif self.left.curType is not Entry.singleton_Integer:  # Rule  No.7
            errMsg = header + "left is not a Entry.singleton_Integer type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif self.right.curType is not Entry.singleton_Integer:
            errMsg = header + "right is not a Entry.singleton_Integer type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        # elif self.op in ["DIV", "MOD"] and isinstance(self.right, Number) and self.right.val is 0:
        #     errMsg = header + "cannot DIV or MOD 0"
        #     myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        else:
            self.curType = Entry.singleton_Integer

    def toString(self):
        posInfo = " Node.Binary @("+str(self.startPos)+", "+str(self.endPos)+")"
        return posInfo + " " + self.op + validStr(self.left) +validStr(self.right) + validStr(self.curType)

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_AST_Binary(self, idx)
        else:
            visitor.Graph_Visit_AST_Binary(self, idx)
         
    def accept_Interpreter(self, visitor):
        visitor.Interpreter_Visit_Binary(self)

    def accept_CodeGen(self, visitor):
        visitor.CodeGen_Visit_Binary(self)


class Condition(Node):
    op = None
    left = None
    right = None
    isValid = False
    myErrHandler = None
    def __init__(self, op, left, right, startPos, endPos, myErrHandler):
        self.op = op
        self.left = left
        self.right = right
        self.startPos = startPos
        self.endPos = endPos
        self.myErrHandler = myErrHandler

        header = "<AST> when constructing [Condition] @("+str(self.startPos)+", "+str(self.endPos)+"), "
        errMsg = ""
        if self.op is None or self.op not in ["=", "#", "<", ">", "<=", ">="]:
            errMsg = header + "op is None or unknown string"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif self.left is None or self.right is None:
            errMsg = header + "left or right is None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

        elif isinstance(self.left, Expression) is False:
            errMsg = header + "left should be a Node.Expression type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif isinstance(self.right, Expression) is False:
            errMsg = header + "right should be a Node.Expression type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

        elif self.left.curType is not Entry.singleton_Integer:  # Rule No.10
            errMsg = header + "left is not a Entry.singleton_Integer type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif self.right.curType is not Entry.singleton_Integer:
            errMsg = header + "right is not a Entry.singleton_Integer type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        else:
            self.isValid = True

    def opposite(self):
        if self.isValid is True:
            opposite_op = None
            if self.op == "=":
                opposite_op = "#"
            elif self.op == "#":
                opposite_op = "="
            elif self.op == ">":
                opposite_op = "<="
            elif self.op == "<":
                opposite_op = ">="
            elif self.op == ">=":
                opposite_op = "<"
            elif self.op == "<=":
                opposite_op = ">"
            return Condition(opposite_op, self.left, self.right, self.startPos, self.endPos, self.myErrHandler)
        else:
            return None


    def toString(self):
        posInfo = " Node.Condition @("+str(self.startPos)+", "+str(self.endPos)+")"
        return posInfo + " " + self.op + validStr(self.left) +validStr(self.right)

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_AST_Condition(self, idx)
        else:
            visitor.Graph_Visit_AST_Condition(self, idx)

    def accept_Interpreter(self, visitor):
        visitor.Interpreter_Visit_Condition(self)

    def accept_CodeGen(self, visitor):
        visitor.CodeGen_Visit_Condition(self)
        

class Instruction(Node):
    startPos = -1
    endPos = -1
    def toString(self):
        pass


class fakeInstruction(Instruction):
    startPos = -1
    endPos = -1
    nextInst = None
    def set_Next_Instruction(self, nextInst):
        self.nextInst = nextInst

    def toString(self):
        return "this is an faked Instruction Node"


class Assign(Instruction):
    location = None
    expression = None
    nextInst = None
    def __init__(self, location, expression, startPos, endPos, myErrHandler):
        self.location = location
        self.expression = expression
        self.startPos = startPos
        self.endPos = endPos

        header = "<AST> when constructing [Assign] @("+str(self.startPos)+", "+str(self.endPos)+"), "
        errMsg = ""
        if self.location is None:
            errMsg = header + "found self.location is None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif self.expression is None:
            errMsg = header + "found self.expression is None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

        elif isinstance(self.location, Location) is False:
            errMsg = header + "found self.location is not a Node.Location type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif isinstance(self.expression, Expression) is False:
            errMsg = header + "found self.expression is not a Node.Expression type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif self.location.curType != self.expression.curType:  # Rule No.9
            errMsg = header + "found self.location.curType is not equal to self.expression.curType"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

    def set_Next_Instruction(self, nextInst):
        self.nextInst = nextInst

    def toString(self):
        posInfo = " Node.Assign @("+str(self.startPos)+", "+str(self.endPos)+")"
        hasNext = "False"
        if self.nextInst != None:
            hasNext = "True"
        return posInfo + " " + validStr(self.location) + validStr(self.expression) + " hasNext: " + hasNext

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_AST_Assign(self, idx)
        else:
            visitor.Graph_Visit_AST_Assign(self, idx)

    def accept_Interpreter(self, visitor):
        visitor.Interpreter_Visit_Assign(self)

    def accept_CodeGen(self, visitor):
        visitor.CodeGen_Visit_Assign(self)


class Read(Instruction):
    location = None
    nextInst = None
    def __init__(self, location, startPos, endPos, myErrHandler):
        self.location = location
        self.startPos = startPos
        self.endPos = endPos

        header = "<AST> when constructing [Read] @("+str(self.startPos)+", "+str(self.endPos)+"), "
        errMsg = ""
        if self.location is None:
            errMsg = header + "found self.location is None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

        elif isinstance(self.location, Location) is False:
            errMsg = header + "found self.location is not a Node.Location type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

        elif self.location.curType != Entry.singleton_Integer:  # Rule No.12
            errMsg = header + "found self.location.curType is not a Entry.singleton_Integer type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

    def set_Next_Instruction(self, nextInst):
        self.nextInst = nextInst

    def toString(self):
        posInfo = " Node.Read @("+str(self.startPos)+", "+str(self.endPos)+")"
        hasNext = "False"
        if self.nextInst != None:
            hasNext = "True"
        return posInfo + " " + validStr(self.location) + " hasNext: " + hasNext

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_AST_Read(self, idx)
        else:
            visitor.Graph_Visit_AST_Read(self, idx)

    def accept_Interpreter(self, visitor):
        visitor.Interpreter_Visit_Read(self)

    def accept_CodeGen(self, visitor):
        visitor.CodeGen_Visit_Read(self)


class Write(Instruction):
    expression = None
    nextInst = None
    def __init__(self, expression, startPos, endPos, myErrHandler):
        self.expression = expression
        self.startPos = startPos
        self.endPos = endPos

        header = "<AST> when constructing [Write] @("+str(self.startPos)+", "+str(self.endPos)+"), "
        errMsg = ""
        if self.expression is None:
            errMsg = header + "found self.expression is None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

        elif isinstance(self.expression, Expression) is False:
            errMsg = header + "found self.expression is not a Node.Expression type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

        elif self.expression.curType != Entry.singleton_Integer:  # Rule No.11
            errMsg = header + "found self.expression.curType is not a Entry.singleton_Integer type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

    def set_Next_Instruction(self, nextInst):
        self.nextInst = nextInst

    def toString(self):
        posInfo = " Node.Read @("+str(self.startPos)+", "+str(self.endPos)+")"
        hasNext = "False"
        if self.nextInst != None:
            hasNext = "True"
        return posInfo + " " + validStr(self.expression) + " hasNext: " + hasNext

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_AST_Write(self, idx)
        else:
            visitor.Graph_Visit_AST_Write(self, idx)

    def accept_Interpreter(self, visitor):
        visitor.Interpreter_Visit_Write(self)

    def accept_CodeGen(self, visitor):
        visitor.CodeGen_Visit_Write(self)


class If(Instruction):
    cond = None
    true_Inst = None
    false_Inst = None
    nextInst = None
    def __init__(self, cond, true_Inst, false_Inst, startPos, endPos, myErrHandler):
        self.cond = cond
        self.true_Inst = true_Inst
        self.false_Inst = false_Inst
        self.startPos = startPos
        self.endPos = endPos

        header = "<AST> when constructing [If] @("+str(self.startPos)+", "+str(self.endPos)+"), "
        errMsg = ""
        if self.cond is None:
            errMsg = header + "found self.cond is None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif self.true_Inst is None:
            errMsg = header + "found self.true_Inst is None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)


        elif isinstance(self.cond, Condition) is False:
            errMsg = header + "found self.cond is not a Node.Condition type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

        elif isinstance(self.true_Inst, Instruction) is False:
            errMsg = header + "found self.true_Inst is not a Node.Instruction type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif self.false_Inst is not None and isinstance(self.false_Inst, Instruction) is False:
            errMsg = header + "found self.false_Inst is not a Node.Instruction type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

    def set_Next_Instruction(self, nextInst):
        self.nextInst = nextInst

    def toString(self):
        posInfo = " Node.If @("+str(self.startPos)+", "+str(self.endPos)+")"
        hasNext = "False"
        if self.nextInst != None:
            hasNext = "True"
        return posInfo + " " + validStr(self.cond) + validStr(self.true_Inst) + validStr(self.false_Inst) + " hasNext: " + hasNext

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_AST_If(self, idx)
        else:
            visitor.Graph_Visit_AST_If(self, idx)

    def accept_Interpreter(self, visitor):
        visitor.Interpreter_Visit_If(self)

    def accept_CodeGen(self, visitor):
        visitor.CodeGen_Visit_If(self)


class Repeat(Instruction):
    cond = None
    inst = None
    nextInst = None
    def __init__(self, cond, inst, startPos, endPos, myErrHandler):
        self.cond = cond
        self.inst = inst
        self.startPos = startPos
        self.endPos = endPos

        header = "<AST> when constructing [Repeat] @("+str(self.startPos)+", "+str(self.endPos)+"), "
        errMsg = ""
        if self.cond is None:
            errMsg = header + "found self.cond is None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)
        elif self.inst is None:
            errMsg = header + "found self.inst is None"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)


        elif isinstance(self.cond, Condition) is False:
            errMsg = header + "found self.cond is not a Node.Condition type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

        elif isinstance(self.inst, Instruction) is False:
            errMsg = header + "found self.inst is not a Node.Instruction type"
            myErrHandler.Record_AST_Err("AST", errMsg, self.startPos)

    def set_Next_Instruction(self, nextInst):
        self.nextInst = nextInst

    def toString(self):
        posInfo = " Node.If @("+str(self.startPos)+", "+str(self.endPos)+")"
        hasNext = "False"
        if self.nextInst != None:
            hasNext = "True"
        return posInfo + " " + validStr(self.cond) + validStr(self.inst) + " hasNext: " + hasNext

    def accept(self, visitor, idx, isGraph):
        if isGraph is False:
            visitor.Visit_AST_Repeat(self, idx)
        else:
            visitor.Graph_Visit_AST_Repeat(self, idx)

    def accept_Interpreter(self, visitor):
        visitor.Interpreter_Visit_Repeat(self)

    def accept_CodeGen(self, visitor):
        visitor.CodeGen_Visit_Repeat(self)



def green(text):
    return "\033[1;32m{}\033[0;0m".format(text)

def red(text):
    return "\033[1;31m{}\033[0;0m".format(text)

def blue(text):
    return "\033[1;34m{}\033[0;0m".format(text)

def validStr(curObj):
    if curObj is None:
        return "None"
    return curObj.toString()
# Unit Test for Node.py
if __name__ == "__main__":
    
    ErrHandler = ErrorHandler.ErrorHandeler("")

    print(red("# Unit test: ")+blue("AST-Variable")) 
    ST_Variable = Entry.Variable(Entry.singleton_Integer)
    print(ST_Variable.toString())
    AST_Variable = Variable(ST_Variable, 0, 1, ErrHandler)
    print(AST_Variable.toString())
    print("")


    print(red("# Unit test: ")+blue("AST-Index")) 
    ST_Constant = Entry.Constant(Entry.singleton_Integer, 10)
    ST_Array = Entry.Array(Entry.singleton_Integer, ST_Constant)
    ST_Variable_Array = Entry.Variable(ST_Array)
    AST_Variable_Array = Variable(ST_Variable_Array, 2, 3, ErrHandler)

    AST_Index = Index(AST_Variable_Array, AST_Variable, 4, 5, ErrHandler)
    print(AST_Index.toString())
    print("")


    print(red("# Unit test: ")+blue("AST-Field")) 
    ST_Scope = Entry.Scope()
    ST_Field_type = Entry.Field(Entry.singleton_Integer)
    AST_test_FVar = Variable(ST_Field_type, 2, 3, ErrHandler)
    ST_Field = Entry.Variable(ST_Field_type)
    ST_Scope.insert("A", ST_Field_type)
    ST_Scope.insert("D", Entry.Field(Entry.Array(Entry.singleton_Integer, ST_Constant)))
    ST_Record_type = Entry.Record(ST_Scope)
    ST_Variable_Record = Entry.Variable(ST_Record_type)
    AST_Variable_Record = Variable(ST_Variable_Record, 6, 7, ErrHandler, "a")
    AST_Variable_Field = Variable(ST_Field, 8, 9, ErrHandler)

    AST_Field = Field(AST_Variable_Record, AST_test_FVar, 10, 11, ErrHandler)
    print(AST_Field.toString())
    print("")


    # print(red("# Unit test: ")+blue("AST-Number")) 
    # ST_Constant = Entry.Constant(Entry.singleton_Integer, 16)
    # print(ST_Constant.toString())
    # AST_Number = Number(ST_Constant, None, 12, 13, ErrHandler)
    # print(AST_Number.toString())
    # val = 17
    # AST_Number2 = Number(None, val, 12, 13, ErrHandler)
    # print(AST_Number2.toString())
    # print("")


    # print(red("# Unit test: ")+blue("AST-Binary")) 
    # AST_Binary = Binary("DIV", AST_Variable, AST_Number2, 14, 15, ErrHandler)
    # print(AST_Binary.toString())
    # print("")


    # print(red("# Unit test: ")+blue("AST-Condition")) 
    # AST_Condition = Condition(">", AST_Variable, AST_Number2, 16, 17, ErrHandler)
    # print(AST_Condition.toString())
    # AST_oppo_Condition = AST_Condition.opposite()
    # print(AST_oppo_Condition.toString())
    # print("")


    # print(red("# Unit test: ")+blue("AST-Assign")) 
    # ST_Constant = Entry.Constant(Entry.singleton_Integer, 10)
    # ST_Array = Entry.Array(Entry.singleton_Integer, ST_Constant)
    # ST_Variable_Array = Entry.Variable(ST_Array)
    # AST_Variable_Array = Variable(ST_Variable_Array, 2, 3, ErrHandler)
    # AST_Assign = Assign(AST_Field, AST_Variable, 18, 19, ErrHandler)
    # print(AST_Assign.toString())
    # print(AST_Field.curType)
    # print(AST_Variable.curType)
    # print("")


    # print(red("# Unit test: ")+blue("AST-Read")) 
    # AST_Read = Read(AST_Variable, 20, 21, ErrHandler)
    # print(AST_Read.toString())
    # print("")


    # print(red("# Unit test: ")+blue("AST-Write")) 
    # AST_Write = Write(AST_Field, 22, 23, ErrHandler)
    # print(AST_Write.toString())
    # print("")


    # print(red("# Unit test: ")+blue("AST-If")) 
    # AST_If = If(AST_Condition, AST_Read, None, 24, 25, ErrHandler)
    # print(AST_If.toString())
    # print("")


    # print(red("# Unit test: ")+blue("AST-Repeat")) 
    # AST_Repeat = Repeat(AST_Condition, AST_Read, 24, 25, ErrHandler)
    # print(AST_Repeat.toString())
    # print("")

    # print(red("# Unit test: ")+blue("AST-ErrInstruction")) 
    # AST_fakeInstruction = fakeInstruction()
    # print(AST_fakeInstruction.toString())
    # print("")

    print(red("### Here are the errors: "))
    ErrHandler.show_AST_err()