# Zifan Yang
# zyang45@jhu.edu
# from Observer import Observer, TextObserver, GraphicObserver
from Token import Token
from Entry import Constant, Variable, Type, Integer, Array, Record, Field, Scope, singleton_Integer
from Visitor import Visitor
import Node


class Parser():

    tokenList = []
    curPos = -1            # the position of current
    current = None         # the current Token : tokenList[curPos]
    last = None            # the last Token:    tokenList[curPos-1]
    ob = None              # observer
    myErrHandler = None    # the object to handle errors
    weakSymbolFlag = True

    Universal_Scope = None
    Program_Scope = None
    Current_Scope = None
    visitor = None          # using visitor pattern to print Symbol Table
    prevEntryName = None

    AST_root = None         # the root Node of AST
    ast_visitor = None
    prevEntryId = None    # using to pass the id to Selector method
    hasBEGIN = False

    def __init__(self, tokenList, myErrHandler):
        # just make sure that all token in tokenList are valid
        for token in tokenList:
            if token is not None:
                self.tokenList.append(token)
        self.curPos = 0
        self.current = self.tokenList[0]
        self.last = None
        self.myErrHandler = myErrHandler

        self.Universal_Scope = Scope()
        self.Universal_Scope.insert("INTEGER", singleton_Integer)
        self.prevEntryName = None

        self.AST_root = None
        self.ast_visitor = None
        self.prevEntryId = None
        self.hasBEGIN = False

    """
    Here is our public function #####
    """
    def parse(self, isGraph=False):
        self.Program_ST()

        self.myErrHandler.show_err()

        if self.visitor is not None:
            self.Program_Scope.accept(self.visitor, 0, isGraph)

        if self.ast_visitor is not None:
            if self.hasBEGIN is True:
                self.ast_visitor.addContent("instructions =>")
                self.AST_root.accept(self.ast_visitor, 1, isGraph)

        return self.Program_Scope, self.AST_root

    """
    Here are Observer stuff #####
    """
    def observed(func):
        def production_wrapper(self):
            funcName = func.__name__
            funcName = funcName[:len(funcName)-3]
            if self.ob is not None:
                self.ob.start(funcName)
            ret = func(self)
            if self.ob is not None:
                self.ob.stop(funcName)
            return ret
        return production_wrapper

    def attach(self, ob):
        self.ob = ob

    def detach(self):
        curOb = self.ob
        self.ob = None
        return curOb

    """
    Here are re-sync strong symbol stuff #####
    """
    def synced(startSet, syncSet):
        def wrapper(func):
            def inner_wrapper(self):
                if self.isInside(self.current, startSet) is False:
                    self.myErrHandler.Record_Err("Parser", "cannot match current token "+self.current.getDescription()+" to "+str(startSet)+" trying to re-sync...", self.curPos)
                    while self.isInside(self.current, syncSet) is False:
                        self.next()
                    if self.isInside(self.current, startSet) is True:
                        ret = func(self)
                    else:
                        ret = None
                else:  # matched and dont need to re-sync
                    ret = func(self)
                return ret
            return inner_wrapper
        return wrapper

    def isInside(self, tmpToken, tokenSet):
        if tmpToken.Type == "identifier":
            if "IDENTIFIER" in tokenSet:
                return True
            else:
                return False
        elif tmpToken.Type == "integer":
            if "INTEGER" in tokenSet:
                return True
            else:
                return False
        elif tmpToken.Type == "eof":
            if "EOF" in tokenSet:
                return True
            else:
                return False
        elif tmpToken.Type == "keyword":
            needToRemoveSet = {"IDENTIFIER", "INTEGER", "EOF"}
            if tmpToken.Value_Str in (tokenSet-needToRemoveSet):
                return True
            else:
                return False
        return False

    """
    Here is fixing missing weak symbol function #####
    """
    def fixMissingWeakSymbol(self, tmpResult, missingTokenStr):
        if self.weakSymbolFlag is True and tmpResult is None:
            missingToken = Token(missingTokenStr, "keyword", -1, -1)
            if self.ob is not None:
                self.ob.match(missingToken)

    """
    Here are our private functions #####
    """
    def next(self):
        self.last = self.current
        self.curPos += 1
        self.current = self.tokenList[self.curPos]

    def match(self, candidateList, isweakSymbol=False):
        curToken = self.current
        if curToken.Type == "eof" and candidateList == ["eof"]:
            return "eof"
        if curToken.Type == "keyword" and curToken.Value_Str in candidateList:
            if self.ob is not None:
                self.ob.match(curToken)
            self.next()
            return curToken.Value_Str
        if curToken.Type == "identifier" and candidateList == ["identifier"]:
            if self.ob is not None:
                self.ob.match(curToken)
            self.next()
            return curToken.Value_Str
        if curToken.Type == "integer" and candidateList == ["integer"]:
            if self.ob is not None:
                self.ob.match(curToken)
            self.next()
            return curToken.Value_Int
        if isweakSymbol is False:
            self.myErrHandler.Record_Err("Parser", "cannot match current token "+curToken.getDescription()+" to "+str(candidateList), self.curPos)
        else:
            self.myErrHandler.Record_Err("Parser", "weak symbol is missing before "+curToken.getDescription(), self.curPos, True)

        return None

    """
    Here are function per grammar rule #####
    """
    @observed
    def Program_ST(self):  # 1. Program = "PROGRAM" identifier ";" Declarations ["BEGIN" Instructions] "END" identifier "."
        self.Program_Scope = Scope(self.Universal_Scope)
        self.Current_Scope = self.Program_Scope

        self.match(["PROGRAM"])
        Program_Identifier_Start = self.match(["identifier"])
        self.match([";"])

        if self.current.Value_Str not in ["BEGIN", "END"]:
            self.Declarations_ST()
        else:
            if self.ob is not None:
                self.ob.start("Declarations")
                self.ob.stop("Declarations")

        if self.current.Type == "keyword" and self.current.Value_Str == "BEGIN":
            self.hasBEGIN = True
            self.match(["BEGIN"])
            self.AST_root = self.Instructions_ST()

        self.match(["END"])
        Program_Identifier_End = self.match(["identifier"])
        self.Check_Program_Identifier(Program_Identifier_Start, Program_Identifier_End, self.myErrHandler)
        self.match(["."])
        self.match(["eof"])


    @synced({"CONST", "TYPE", "VAR"}, {"CONST", "TYPE", "VAR", "BEGIN", "EOF"})
    @observed
    def Declarations_ST(self):    # 2, Declarations = { ConstDecl | TypeDecl | VarDecl }
        while self.current.Type == "keyword" and (self.current.Value_Str in ["CONST", "TYPE", "VAR"]):
            if self.current.Value_Str == "CONST":
                self.ConstDecl_ST()
            elif self.current.Value_Str == "TYPE":
                self.TypeDecl_ST()
            elif self.current.Value_Str == "VAR":
                self.VarDecl_ST()


    @observed
    def ConstDecl_ST(self):  # 3. ConstDecl = "CONST" {identifier "=" Expression ";"}
        self.match(["CONST"])
        while self.current.Type == "identifier":
            key = self.match(["identifier"])
            tmpResult = self.match(["="], isweakSymbol=True)
            self.fixMissingWeakSymbol(tmpResult, "=")
            tmpStartPos = self.curPos
            exp_node = self.Expression_ST()
            self.match([";"])
            tmpEndPos = self.curPos - 1
            val = self.Check_const_and_get_ST(exp_node, tmpStartPos, tmpEndPos, self.myErrHandler)
            self.Insert_Into_Scope(key, val, self.myErrHandler)


    @observed
    def TypeDecl_ST(self):    # 4. TypeDecl = "TYPE" {identifier "=" Type ";"}
        self.match(["TYPE"])
        while self.current.Type == "identifier":
            tmpStartPos = self.curPos
            key = self.match(["identifier"])
            tmpResult = self.match(["="], isweakSymbol=True)
            self.fixMissingWeakSymbol(tmpResult, "=")
            val = self.Type_ST()
            self.match([";"])
            tmpEndPos = self.curPos - 1
            self.Insert_Into_Scope(key, val, self.myErrHandler)


    @observed
    def VarDecl_ST(self):    # 5. VarDecl = "VAR" {IdentifierList ":" Type ";"}
        self.match(["VAR"])
        while self.current.Type == "identifier":
            tmpStartPos = self.curPos
            IdList = self.IdentifierList_ST()
            tmpResult = self.match([":"], isweakSymbol=True)
            self.fixMissingWeakSymbol(tmpResult, ":")
            typeObj = self.Type_ST()
            self.match([";"])
            tmpEndPos = self.curPos - 1
            VarObj = None
            # if typeObj is not None:
            #     VarObj = Variable(typeObj, tmpStartPos, tmpEndPos)
            for key in IdList:
                if typeObj is not None:
                    self.Insert_Into_Scope(key, Variable(typeObj, tmpStartPos, tmpEndPos), self.myErrHandler)


    @synced({"IDENTIFIER", "ARRAY", "RECORD"}, {"IDENTIFIER", "ARRAY", "RECORD", "CONST", "TYPE", "VAR", "BEGIN" "EOF"})
    @observed
    def Type_ST(self):    # 6. Type = identifier | "ARRAY" Expression "OF" Type | "RECORD" {IdentifierList ":" Type ";"} "END"
        if self.current.Type == "identifier":
            tmpStartPos = self.curPos
            key = self.match(["identifier"])
            return self.Get_Key_In_Current_Scope(key, tmpStartPos, self.myErrHandler)
        elif self.current.Type == "keyword" and self.current.Value_Str == "ARRAY":
            tmpStartPos = self.curPos
            self.match(["ARRAY"])
            exp_node = self.Expression_ST()
            tmpEndPos = self.curPos - 1
            lengthConst = self.Check_const_gt_zero_and_get_ST(exp_node, tmpStartPos, tmpEndPos, self.myErrHandler)
            self.match(["OF"])
            typeObj = self.Type_ST()
            tmpEndPos = self.curPos - 1
            if typeObj is not None:
                return Array(typeObj, lengthConst, tmpStartPos, tmpEndPos)
            else:
                return None
        elif self.current.Type == "keyword" and self.current.Value_Str == "RECORD":
            tmpStartPos = self.curPos
            self.match(["RECORD"])
            Record_Scope = Scope(self.Current_Scope)
            self.Current_Scope = Record_Scope
            while self.current.Type == "identifier":
                innerStartPos = self.curPos
                IdList = self.IdentifierList_ST()
                tmpResult = self.match([":"], isweakSymbol=True)
                self.fixMissingWeakSymbol(tmpResult, ":")
                typeObj = self.Type_ST()
                self.match([";"])
                innerEndPos = self.curPos - 1
                FieldObj = None
                # if typeObj is not None:
                #     FieldObj = Field(typeObj, innerStartPos, innerEndPos)
                for key in IdList:
                    if typeObj is not None:
                        self.Insert_Into_Scope(key, Field(typeObj, innerStartPos, innerEndPos), self.myErrHandler)
            tmpResult = self.match(["END"], isweakSymbol=True)
            self.fixMissingWeakSymbol(tmpResult, "END")
            tmpEndPos = self.curPos - 1
            resultRecord = Record(self.Current_Scope, tmpStartPos, tmpEndPos)
            self.Current_Scope = self.Current_Scope.outerScope
            resultRecord.scopePtr.outerScope = None
            return resultRecord
        else:
            self.myErrHandler.Record_Err("Parser", "cannot match current token "+self.current.getDescription()+" to "+"identifier or ARRAY or RECORD", self.curPos)
            # self.next()


    @observed
    def Expression_ST(self):  # 7. Expression = ["+"|"-"] Term {("+"|"-") Term}
        tmpStartPos = self.curPos

        op = None
        zero_num_node = Node.Number(None, 0, tmpStartPos, tmpStartPos, self.myErrHandler)
        if self.current.Type == "keyword" and self.current.Value_Str in ["+", "-"]:
            op = self.match(["+", "-"])
        ret_node = self.Term_ST()
        tmpEndPos = self.curPos - 1
        if op == "-":
            if isinstance(ret_node, Node.Number):
                ret_node = self.Constant_Folding(op, zero_num_node, ret_node, tmpStartPos, tmpEndPos, self.myErrHandler)
            else:
                ret_node = Node.Binary(op, zero_num_node, ret_node, tmpStartPos, tmpEndPos, self.myErrHandler)

        while self.current.Type == "keyword" and self.current.Value_Str in ["+", "-"]:
            op = self.match(["+", "-"])
            Right_node = self.Term_ST()
            tmpEndPos = self.curPos - 1
            if isinstance(ret_node, Node.Number) and isinstance(Right_node, Node.Number):  # Constant folding
                ret_node = self.Constant_Folding(op, ret_node, Right_node, tmpStartPos, tmpEndPos, self.myErrHandler)
            else:
                ret_node = Node.Binary(op, ret_node, Right_node, tmpStartPos, tmpEndPos, self.myErrHandler)
        return ret_node


    @observed
    def Term_ST(self):    # 8. Term = Factor {("*"|"DIV"|"MOD") Factor}
        tmpStartPos = self.curPos

        ret_node = self.Factor_ST()
        while self.current.Type == "keyword" and self.current.Value_Str in ["*", "DIV", "MOD"]:
            op = self.match(["*", "DIV", "MOD"])
            Right_node = self.Factor_ST()
            tmpEndPos = self.curPos - 1

            if isinstance(ret_node, Node.Number) and isinstance(Right_node, Node.Number):  # Constant folding
                ret_node = self.Constant_Folding(op, ret_node, Right_node, tmpStartPos, tmpEndPos, self.myErrHandler)
            else:
                ret_node = Node.Binary(op, ret_node, Right_node, tmpStartPos, tmpEndPos, self.myErrHandler)

        return ret_node

    @synced({"IDENTIFIER", "INTEGER", "("}, {"IDENTIFIER", "INTEGER", "(", "EOF"})
    @observed
    def Factor_ST(self):  # 9. Factor = integer | Designator | "(" Expression ")"
        tmpStartPos = self.curPos

        ret_AST_node = None
        if self.current.Type == "integer":
            val = self.match(["integer"])
            tmpEndPos = self.curPos - 1
            ret_AST_node = Node.Number(None, val, tmpStartPos, tmpEndPos, self.myErrHandler)

        elif self.current.Type == "identifier":
            ret_AST_node = self.Designator_ST()
            tmpEndPos = self.curPos - 1
            ret_AST_node = self.Check_is_Var_or_Const(ret_AST_node, tmpStartPos, tmpEndPos, self.myErrHandler)
        elif self.current.Type == "keyword" and self.current.Value_Str == "(":
            self.match(["("])
            ret_AST_node = self.Expression_ST()
            tmpResult = self.match([")"], isweakSymbol=True)
            self.fixMissingWeakSymbol(tmpResult, ")")
            tmpEndPos = self.curPos - 1
        else:
            self.myErrHandler.Record_Err("Parser", "cannot match current token "+self.current.getDescription()+" to "+"integer or identifier or (", self.curPos)
            ret_AST_node = Node.fakeExpression()
            tmpEndPos = self.curPos - 1

        return ret_AST_node


    @observed
    def Instructions_ST(self):  # 10. Instructions = Instruction {";" Instruction}
        headNode = self.Instruction_ST()
        tailNode = headNode
        while self.current.Type == "keyword" and self.current.Value_Str == ";":
            self.match([";"])
            curNode = self.Instruction_ST()
            tailNode.set_Next_Instruction(curNode)
            tailNode = curNode
        return headNode


    @synced({"IDENTIFIER", "IF", "WHILE", "REPEAT", "READ", "WRITE"}, {"IDENTIFIER", "IF", "WHILE", "REPEAT", "READ", "WRITE", "EOF"})
    @observed
    def Instruction_ST(self):  # 11. Instruction = Assign | If | Repeat | While | Read | Write
        Inst_node = None
        if self.current.Type == "identifier":
            Inst_node = self.Assign_ST()
        elif self.current.Type == "keyword" and self.current.Value_Str == "IF":
            Inst_node = self.If_ST()
        elif self.current.Type == "keyword" and self.current.Value_Str == "REPEAT":
            Inst_node = self.Repeat_ST()
        elif self.current.Type == "keyword" and self.current.Value_Str == "WHILE":
            Inst_node = self.While_ST()
        elif self.current.Type == "keyword" and self.current.Value_Str == "READ":
            Inst_node = self.Read_ST()
        elif self.current.Type == "keyword" and self.current.Value_Str == "WRITE":
            Inst_node = self.Write_ST()
        else:
            self.myErrHandler.Record_Err("Parser", "cannot match current token "+self.current.getDescription()+" to "+"identifier or IF or REPEAT or WHILE or READ or WRITE", self.curPos)
            Inst_node = Node.fakeInstruction()
        return Inst_node


    @observed
    def Assign_ST(self):  # 12. Assign = Designator ":=" Expression
        tmpStartPos = self.curPos
        
        Location_node = self.Designator_ST()
        tmpResult = self.match([":="], isweakSymbol=True)
        if self.weakSymbolFlag is True and tmpResult is None and self.current.Type == "keyword" and self.current.Value_Str == "=":
            self.fixMissingWeakSymbol(tmpResult, ":=")
            self.next()
        Expression_node = self.Expression_ST()
        
        tmpEndPos = self.curPos - 1
        return Node.Assign(Location_node, Expression_node, tmpStartPos, tmpEndPos, self.myErrHandler)


    @observed
    def If_ST(self):  # 13. If = "IF" Condition "THEN" Instructions ["ELSE" Instructions] "END"
        tmpStartPos = self.curPos
        
        self.match(["IF"])
        Cond_node = self.Condition_ST()
        tmpResult = self.match(["THEN"], isweakSymbol=True)
        self.fixMissingWeakSymbol(tmpResult, "THEN")
        True_node = self.Instructions_ST()
        False_node = None
        if self.current.Type == "keyword" and self.current.Value_Str == "ELSE":
            self.match(["ELSE"])
            False_node = self.Instructions_ST()
        tmpResult = self.match(["END"], isweakSymbol=True)
        self.fixMissingWeakSymbol(tmpResult, "END")
        
        tmpEndPos = self.curPos - 1
        return Node.If(Cond_node, True_node, False_node, tmpStartPos, tmpEndPos, self.myErrHandler)


    @observed
    def Repeat_ST(self):  # 14. Repeat = "REPEAT" Instructions "UNTIL" Condition "END"
        tmpStartPos = self.curPos
        
        self.match(["REPEAT"])
        Inst_node = self.Instructions_ST()
        self.match(["UNTIL"])
        Cond_node = self.Condition_ST()
        tmpResult = self.match(["END"], isweakSymbol=True)
        self.fixMissingWeakSymbol(tmpResult, "END")

        tmpEndPos = self.curPos - 1
        return Node.Repeat(Cond_node, Inst_node, tmpStartPos, tmpEndPos, self.myErrHandler)


    @observed
    def While_ST(self):  # 15. While = "WHILE" Condition "DO" Instructions "END"
        tmpStartPos = self.curPos

        self.match(["WHILE"])
        Cond_node = self.Condition_ST()
        oppo_Cond_node = Cond_node.opposite()
        tmpResult = self.match(["DO"], isweakSymbol=True)
        self.fixMissingWeakSymbol(tmpResult, "DO")
        Inst_node = self.Instructions_ST()
        tmpResult = self.match(["END"], isweakSymbol=True)
        self.fixMissingWeakSymbol(tmpResult, "END")

        tmpEndPos = self.curPos - 1
        repeat_inst = Node.Repeat(oppo_Cond_node, Inst_node, tmpStartPos, tmpEndPos, self.myErrHandler)
        return Node.If(Cond_node, repeat_inst, None, tmpStartPos, tmpEndPos, self.myErrHandler)


    @observed
    def Condition_ST(self):  # 16. Condition = Expression ("="|"#"|"<"|">"|"<="|">=") Expression
        tmpStartPos = self.curPos

        Left_node = self.Expression_ST()
        op = None
        if self.current.Type == "keyword" and self.current.Value_Str in ["=", "#", "<", ">", "<=", ">="]:
            op = self.match(["=", "#", "<", ">", "<=", ">="])
        else:
            self.myErrHandler.Record_Err("Parser", "cannot match current token "+self.current.getDescription()+" to "+"=, #, <, >, <=, >=", self.curPos)
        Right_node = self.Expression_ST()

        tmpEndPos = self.curPos - 1
        return Node.Condition(op, Left_node, Right_node, tmpStartPos, tmpEndPos, self.myErrHandler)


    @observed
    def Write_ST(self):  # 17. Write = "WRITE" Expression
        tmpStartPos = self.curPos

        self.match(["WRITE"])
        Expression_node = self.Expression_ST()

        tmpEndPos = self.curPos - 1
        return Node.Write(Expression_node, tmpStartPos, tmpEndPos, self.myErrHandler)


    @observed
    def Read_ST(self):  # 18. Read = "READ" Designator
        tmpStartPos = self.curPos

        self.match(["READ"])
        Location_node = self.Designator_ST()

        tmpEndPos = self.curPos - 1
        return Node.Read(Location_node, tmpStartPos, tmpEndPos, self.myErrHandler)


    @observed
    def Designator_ST(self):  # 19. Designator = identifier Selector
        tmpStartPos = self.curPos
        curIdentifier = self.match(["identifier"])
        self.prevEntryName = self.Check_Identifier_Valid(curIdentifier, tmpStartPos, self.myErrHandler)
        self.prevEntryId = curIdentifier
        ret_node = self.Selector_ST()
        self.prevEntryName = None
        self.prevEntryId = None

        return ret_node


    @observed
    def Selector_ST(self):  # 20. Selector = {"[" ExpressionList "]" | "." identifier}
        topVar = self.prevEntryName  # this can only be Constant or Variable
        topId = self.prevEntryId
        self.prevEntryName = None
        self.prevEntryId = None
        orgScope = self.Current_Scope
        selScope = self.Current_Scope
        Var_node = None
        if isinstance(topVar, Constant) is True :
            Var_node = Node.Number(topVar, None, self.curPos, self.curPos, self.myErrHandler)
        elif isinstance(topVar, Variable) is True:
            Var_node = Node.Variable(topVar, self.curPos, self.curPos, self.myErrHandler, topId)
            # if isinstance(Var_node.curType, Record):
            #     self.Current_Scope = topVar.typePtr.scopePtr

        lastToken = self.last
        while (self.current.Type == "keyword" and self.current.Value_Str == "[") or (self.current.Type == "keyword" and self.current.Value_Str == "."):
            tmpStartPos = self.curPos

            if self.current.Type == "keyword" and self.current.Value_Str == "[":  # Array case
                # self.Check_Is_Array(selScope, lastToken, tmpStartPos, self.myErrHandler)
                self.New_Check_Is_Array(Var_node, tmpStartPos, self.myErrHandler)
                self.match(["["])
                exp_list = self.ExpressionList_ST()
                tmpResult = self.match(["]"], isweakSymbol=True)
                self.fixMissingWeakSymbol(tmpResult, "]")

                for tmpExp in exp_list:
                    if tmpExp is not None:
                        Var_node = Node.Index(Var_node, tmpExp, tmpExp.startPos, tmpExp.endPos, self.myErrHandler)

            elif self.current.Type == "keyword" and self.current.Value_Str == ".":  # Record case
                # selScope = self.Check_Is_RECORD(selScope, lastToken, tmpStartPos, self.myErrHandler)
                selScope = self.New_Check_Is_RECORD(selScope, Var_node, tmpStartPos, self.myErrHandler)
                self.match(["."])
                tmpStartPos = self.curPos
                fieldName = self.match(["identifier"])
                tmpEndPos = self.curPos - 1

                if selScope is not None:
                    cur_ST_field = self.Check_Field_Name(selScope, fieldName, tmpStartPos, self.myErrHandler)
                    ast_var_field = Node.Variable(cur_ST_field, tmpStartPos, tmpEndPos, self.myErrHandler, fieldName)
                    Var_node = Node.Field(Var_node, ast_var_field, tmpStartPos, tmpEndPos, self.myErrHandler)

            else:
                self.myErrHandler.Record_Err("Parser", "cannot match current token "+self.current.getDescription()+" to "+"[ or .", self.curPos)
        
        self.Current_Scope = orgScope
        return Var_node


    @observed
    def IdentifierList_ST(self):  # 21. IdentifierList = identifier {"," identifier}
        resList = []
        curId = self.match(["identifier"])
        if curId is not None:
            resList.append(curId)
        while self.current.Type == "keyword" and self.current.Value_Str == ",":
            self.match([","])
            curId = self.match(["identifier"])
            if curId is not None:
                resList.append(curId)
        return resList


    @observed
    def ExpressionList_ST(self):  # 22. ExpressionList = Expression {"," Expression}
        ret_list = []
        ret_list.append(self.Expression_ST())
        while self.current.Type == "keyword" and self.current.Value_Str == ",":
            self.match([","])
            ret_list.append(self.Expression_ST())
        return ret_list


    """
    Here are functions used in symbol table construction AS3 #####
    """
    def Insert_Into_Scope(self, key, value, errHandler):
        curScope = self.Current_Scope
        if key is None:  # match("indentifier") returns None"
            errMsg = "No key(identifier) founded @("+str(value.startPos)+", "+str(value.endPos)+")"
            errHandler.Record_ST_Err("SymbolTable", errMsg, self.curPos)
            return False
        if value is None:  
            errMsg = "No value founded in key "+str(key)+" @("+str(self.curPos)+")"
            errHandler.Record_ST_Err("SymbolTable", errMsg, self.curPos)
            return False
        if curScope is None:  # scope is None
            errMsg = "No Scope founded when insert ["+key+"] @("+str(value.startPos)+", "+str(value.endPos)+")"
            errHandler.Record_ST_Err("SymbolTable", errMsg, self.curPos)
            return False
        if curScope.local(key) is True:  # the key is already in this scope
            dupKey = curScope.find(key)
            oldStartPos = dupKey.startPos
            oldEndPos = dupKey.endPos
            errMsg = "When inserting ["+key+"] @("+str(value.startPos)+", "+str(value.endPos)+"), the ["+key+"] already exists in @("+str(oldStartPos)+", "+str(oldEndPos)+")"
            errHandler.Record_ST_Err("SymbolTable", errMsg, self.curPos)
            return False
        curScope.insert(key, value)
        return True

    def Get_Key_In_Current_Scope(self, key, startPos, errHandler):
        curScope = self.Current_Scope
        if key is None:  # match("indentifier") returns None"
            errMsg = "No key(identifier) founded @("+str(startPos)+")"
            errHandler.Record_ST_Err("SymbolTable", errMsg, self.curPos)
            return None
        if curScope is None:  # scope is None
            errMsg = "No Scope founded when getting ["+key+"] @("+str(startPos)+")"
            errHandler.Record_ST_Err("SymbolTable", errMsg, self.curPos)
            return None
        returnType = curScope.find(key)
        if returnType is None:  # the key is not in this scope
            errMsg = "Cannot find Type: ["+key+"] @("+str(startPos)+") in the current scope"
            errHandler.Record_ST_Err("SymbolTable", errMsg, self.curPos)
            return None
        # Context Condition rule No.4
        if isinstance(returnType, Type) is False:  # the return Type is not an instance of Type
            errMsg = "The type of ["+key+"] @("+str(startPos)+") is not an instance of \"Type\""
            errHandler.Record_ST_Err("SymbolTable", errMsg, self.curPos)
            return None
        return returnType

    # Context Condition rule No.3
    def Check_Program_Identifier(self, Program_Identifier_Start, Program_Identifier_End, errHandler):
        if Program_Identifier_Start is not None and Program_Identifier_End is not None:
            if Program_Identifier_Start != Program_Identifier_End:
                errMsg = "Cannot match Program Identifier from \" "+str(Program_Identifier_Start)+" \" to \" "+str(Program_Identifier_End)+" \""
                errHandler.Record_ST_Err("SymbolTable", errMsg, self.curPos)


    def Check_Identifier_Valid(self, key, startPos, errHandler):
        curScope = self.Current_Scope
        if key is None:  # match("indentifier") returns None"
            errMsg = "No key(indentifier) founded @("+str(startPos)+")"
            errHandler.Record_ST_Err("SymbolTable", errMsg, self.curPos)
            return None
        if curScope is None:  # scope is None
            errMsg = "No Scope founded when getting ["+key+"] @("+str(startPos)+")"
            errHandler.Record_ST_Err("SymbolTable", errMsg, self.curPos)
            return None
        returnType = curScope.find(key)
        if returnType is None:  # the key is not in this scope
            errMsg = "Cannot find Identifier: ["+key+"] @("+str(startPos)+") in the current scope\n"+curScope.toString()
            errHandler.Record_ST_Err("SymbolTable", errMsg, self.curPos)
            return None
        elif isinstance(returnType, Type) is True:  # Rule No.13
            errMsg = "["+key+"] @("+str(startPos)+") should denote a variable or a constant but not a type"
            errHandler.Record_AST_Err("AST", errMsg, self.curPos)
            return None
        return returnType


    def Check_Is_Array(self, selScope, lastToken, startPos, errHandler):
        curScope = selScope
        key = lastToken.Value_Str
        returnType = curScope.find(key)

        if returnType is None or (isinstance(returnType, Variable) is False and isinstance(returnType, Field) is False) or isinstance(returnType.typePtr, Array) is False:  # the key is not in this scope or is not ARRAY
            errMsg = "\" "+str(key)+" \""+" is not an Array Type Variable @("+str(startPos)+")"
            errHandler.Record_ST_Err("SymbolTable", errMsg, startPos)
            return None

    def New_Check_Is_Array(self, Var_node, startPos, errHandler):
        if Var_node is None:
            return None
        if isinstance(Var_node.curType, Array) is False:
            errMsg = "\" "+str(Var_node)+" \""+" is not an Array Type Variable @("+str(startPos)+")"
            errHandler.Record_ST_Err("SymbolTable", errMsg, startPos)
            return None

    def Check_Is_RECORD(self, selScope, lastToken, startPos, errHandler):
        curScope = selScope
        key = lastToken.Value_Str
        returnType = curScope.find(key)

        if returnType is None or isinstance(returnType, Variable) is False or isinstance(returnType.typePtr, Record) is False:  # the key is not in this scope or is not Record
            errMsg = "\" "+str(key)+" \""+" is not an Record Type Variable @("+str(startPos)+")"
            errHandler.Record_ST_Err("SymbolTable", errMsg, startPos)
            return None
        return returnType.typePtr.scopePtr

    def New_Check_Is_RECORD(self, selScope, Var_node, startPos, errHandler):
        if Var_node is None:
            return None
        if isinstance(Var_node.curType, Record) is False:
            errMsg = "\" "+str(Var_node)+" \""+" is not an Record Type Variable @("+str(startPos)+")"
            errHandler.Record_ST_Err("SymbolTable", errMsg, startPos)
            return None
        return Var_node.curType.scopePtr




    def Check_Field_Name(self, selScope, fieldName, startPos, errHandler):
        curScope = selScope
        key = fieldName
        returnType = curScope.find(key)

        if returnType is None or isinstance(returnType, Field) is False:
            errMsg = "\" "+str(key)+" \""+" is not a field inside current Record @("+str(startPos)+")"
            errHandler.Record_ST_Err("SymbolTable", errMsg, startPos)
            return None
        return returnType


    def Constant_Folding(self, op, left, right, startPos, endPos, errHandler):
        if op is None:
            errMsg = "found unknown op which is None @("+str(startPos)+", "+str(endPos)+")"
            errHandler.Record_AST_Err("AST", errMsg, startPos)
            return left
        if op is "*":
            val = left.val * right.val
            return Node.Number(None, val, startPos, endPos, errHandler)
        elif op == "DIV":
            if right.val == 0:
                errMsg = "cannot DIV 0 @("+str(startPos)+", "+str(endPos)+")"
                errHandler.Record_AST_Err("AST", errMsg, startPos)
                return left
            else:
                val = left.val / right.val
                return Node.Number(None, val, startPos, endPos, errHandler)
        elif op == "MOD":
            if right.val == 0:
                errMsg = "cannot MOD 0 @("+str(startPos)+", "+str(endPos)+")"
                errHandler.Record_AST_Err("AST", errMsg, startPos)
                return left
            else:
                val = left.val % right.val
                return Node.Number(None, val, startPos, endPos, errHandler)
        elif op is "+":
            val = left.val + right.val
            return Node.Number(None, val, startPos, endPos, errHandler)
        elif op is "-":
            val = left.val - right.val
            return Node.Number(None, val, startPos, endPos, errHandler)
        else:
            errMsg = "[critical] unknown op "+str(op)+" @("+str(startPos)+", "+str(endPos)+")"
            errHandler.Record_AST_Err("AST", errMsg, startPos)
            return left


    def Check_const_and_get_ST(self, exp_node, startPos, endPos, errHandler):  # Rule No.5
        fake_const = Constant(singleton_Integer, 5, startPos, endPos)
        if exp_node is None:
            errMsg = "in constDecl, the right hand side is None @("+str(startPos)+", "+str(endPos)+")"
            errHandler.Record_AST_Err("AST", errMsg, startPos)
            return fake_const

        if isinstance(exp_node, Node.Number) is False and isinstance(exp_node, Node.Variable) is False:
            errMsg = "in constDecl, the right hand side is not a Node.Number or Node.Variable type @("+str(startPos)+", "+str(endPos)+")"
            errHandler.Record_AST_Err("AST", errMsg, startPos)
            return fake_const

        if isinstance(exp_node.ST, Constant) is False:
            errMsg = "in constDecl, the right hand side is not a Constant @("+str(startPos)+", "+str(endPos)+")"
            errHandler.Record_AST_Err("AST", errMsg, startPos)
            return fake_const

        if exp_node.curType != singleton_Integer:
            errMsg = "in constDecl, the right hand side is not Integer type @("+str(startPos)+", "+str(endPos)+")"
            errHandler.Record_AST_Err("AST", errMsg, startPos)
            return fake_const
        exp_node.ST.startPos = startPos
        exp_node.ST.endPos = endPos
        return exp_node.ST


    def Check_const_gt_zero_and_get_ST(self, exp_node, startPos, endPos, errHandler):  # Rule No.6
        fake_const = Constant(singleton_Integer, 5, startPos, endPos)
        if exp_node is None:
            errMsg = "in TypeDecl, the Array_size is None @("+str(startPos)+", "+str(endPos)+")"
            errHandler.Record_AST_Err("AST", errMsg, startPos)
            return fake_const

        if isinstance(exp_node, Node.Number) is False and isinstance(exp_node, Node.Variable) is False:
            errMsg = "in TypeDecl, the Array_size is not a Node.Number or Node.Variable type @("+str(startPos)+", "+str(endPos)+")"
            errHandler.Record_AST_Err("AST", errMsg, startPos)
            return fake_const

        if isinstance(exp_node.ST, Constant) is False:
            errMsg = "in TypeDecl, the Array_size is not a Constant @("+str(startPos)+", "+str(endPos)+")"
            errHandler.Record_AST_Err("AST", errMsg, startPos)
            return fake_const

        if exp_node.curType != singleton_Integer:
            errMsg = "in TypeDecl, the Array_size is not Integer type @("+str(startPos)+", "+str(endPos)+")"
            errHandler.Record_AST_Err("AST", errMsg, startPos)
            return fake_const

        if exp_node.ST.val <= 0:
            errMsg = "in TypeDecl, the Array_size must greater than 0 @("+str(startPos)+", "+str(endPos)+")"
            errHandler.Record_AST_Err("AST", errMsg, startPos)
            return fake_const

        return exp_node.ST


    def Check_is_Var_or_Const(self, desig_node, startPos, endPos, errHandler):  # Rule No.8
        fake_const =  Node.Number(None, 5, startPos, endPos, errHandler)
        if desig_node is None:
            errMsg = "in Factor production, the designator is None @("+str(startPos)+", "+str(endPos)+")"
            errHandler.Record_AST_Err("AST", errMsg, startPos)
            return fake_const

        # if isinstance(desig_node, Node.Number) is False and isinstance(desig_node, Node.Variable) is False:
        if isinstance(desig_node, Node.Expression) is False:
            errMsg = "in Factor production, the designator is not a Node.Number or Node.Variable type @("+str(startPos)+", "+str(endPos)+")"
            errHandler.Record_AST_Err("AST", errMsg, startPos)
            return fake_const

        if isinstance(desig_node, Node.Number) is True or isinstance(desig_node, Node.Variable) is True:
            if isinstance(desig_node.ST, Type) is True:
                errMsg = "in Factor production, the designator's type cannot be not Entry.Type @("+str(startPos)+", "+str(endPos)+")"
                errHandler.Record_AST_Err("AST", errMsg, startPos)
                return fake_const

        return desig_node


    def attach_visitor(self, visitor):
        self.visitor = visitor


    def attach_ast_visitor(self, visitor):
        self.ast_visitor = visitor