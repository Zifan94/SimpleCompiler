# Zifan Yang
# zyang45@jhu.edu
import collections
from Entry import singleton_Integer
from Stack import *

class Visitor():
    content = ""
    nodeCnt = 0
    clusterCnt = 0
    graphContent = ""
    lastNode = None
    integer_node = False
    str_obj_dict = {}
    dummyHeadNodeDict = {}
    scopeNodeListDict = {}
    ast_sk = None
    def __init__(self):
        self.content = ""
        self.nodeCnt = 0
        self.clusterCnt = 0
        self.graphContent = "strict digraph Symbol_Table_Graph {\n"
        self.lastNode = None
        self.integer_node = False
        self.str_obj_dict[singleton_Integer.toString()] = "N_INT"
        self.dummyHeadNodeDict = {}
        self.scopeNodeListDict = {}
        self.ast_sk = Stack()

    def addContent(self, tmpContent):
        self.content = self.content+tmpContent+"\n"

    def addGraph(self, tmpContent):
        self.graphContent = self.graphContent+tmpContent+"\n"

    def getTmpNode(self, obj):
        tmpNode = ""
        if self.str_obj_dict.has_key(obj.toString()) is True:
            tmpNode = self.str_obj_dict[obj.toString()]
        else:
            tmpNode = self.nextNode()
            self.str_obj_dict[obj.toString()] = tmpNode
        return tmpNode

    def nextNode(self):
        ret = "N_"+str(self.nodeCnt)
        self.nodeCnt += 1
        return ret

    def nextCluster(self):
        ret = "cluster_"+str(self.nodeCnt)
        self.clusterCnt += 1
        return ret

    def show_content(self):
        return self.content[0:len(self.content)-1]

    def show_graph(self):
        self.addGraph("}")
        return self.graphContent[0:len(self.graphContent)-1]


    def Visit_Scope(self, curScope, idx):
        # curScope.LocalDict = collections.OrderedDict(sorted(curScope.LocalDict.items()))
        self.addContent("  "*idx+"SCOPE BEGIN")
        for key in curScope.LocalDict:
            self.addContent("  "*(idx+1) + str(key) + " =>")
            curScope.LocalDict.get(key).accept(self, idx+2, False)
        self.addContent("  "*idx+"END SCOPE")

    def Visit_Field(self, curField, idx):
        self.addContent("  "*idx+"VAR BEGIN")
        self.addContent("  "*(idx+1) + "type:")
        curField.typePtr.accept(self, idx+2, False)
        self.addContent("  "*idx+"END VAR")

    def Visit_Record(self, curRecord, idx):
        self.addContent("  "*idx+"RECORD BEGIN")
        curRecord.scopePtr.accept(self, idx+1, False)
        self.addContent("  "*idx+"END RECORD")

    def Visit_Array(self, curArray, idx):
        self.addContent("  "*idx+"ARRAY BEGIN")
        self.addContent("  "*(idx+1) + "type:")
        curArray.typePtr.accept(self, idx+2, False)
        self.addContent("  "*(idx+1) + "length:")
        self.addContent("  "*(idx+2) + str(curArray.length.val))
        self.addContent("  "*idx+"END ARRAY")

    def Visit_Integer(self, curInteger, idx):
        self.addContent("  "*idx+"INTEGER")

    def Visit_Variable(self, curVariable, idx):
        self.addContent("  "*idx+"VAR BEGIN")
        self.addContent("  "*(idx+1) + "type:")
        curVariable.typePtr.accept(self, idx+2, False)
        self.addContent("  "*idx+"END VAR")

    def Visit_Constant(self, curConstant, idx):
        self.addContent("  "*idx+"CONST BEGIN")
        self.addContent("  "*(idx+1) + "type:")
        curConstant.typePtr.accept(self, idx+2, False)
        self.addContent("  "*(idx+1) + "value:")
        self.addContent("  "*(idx+2) + str(curConstant.val))
        self.addContent("  "*idx+"END CONST")
    
    """
    Graphic Output
    
    """
    def Graph_Visit_Scope(self, curScope, idx):
        curScope.LocalDict = collections.OrderedDict(sorted(curScope.LocalDict.items()))

        clusterName = ""
        dummyHeadNode = ""
        nodeList = []
        if self.str_obj_dict.has_key(curScope.toString()) is True:
            clusterName = self.str_obj_dict[curScope.toString()]
            dummyHeadNode = self.dummyHeadNodeDict[clusterName]
            nodeList = self.scopeNodeListDict[clusterName]
        else:
            clusterName = self.nextCluster()
            self.addGraph("  subgraph "+clusterName+" {")
            dummyHeadNode = self.nextNode()
            self.addGraph("    "+dummyHeadNode+" [label=\"\", shape=none];")

            nodeList = []

            for key in curScope.LocalDict:
                tmpNode = self.nextNode()
                nodeList.append(tmpNode)
                self.addGraph("    "+tmpNode+" [label=\""+str(key)+"\", shape=none];")
            self.addGraph("  }")
            self.str_obj_dict[curScope.toString()] = clusterName
            self.dummyHeadNodeDict[clusterName] = dummyHeadNode
            self.scopeNodeListDict[clusterName] = nodeList

        # clusterName = self.nextCluster()
        # self.addGraph("  subgraph "+clusterName+" {")
        # dummyHeadNode = self.nextNode()
        # self.addGraph("    "+dummyHeadNode+" [label=\"\", shape=none];")

        # nodeList = []

        # for key in curScope.LocalDict:
        #     tmpNode = self.nextNode()
        #     nodeList.append(tmpNode)
        #     self.addGraph("    "+tmpNode+" [label=\""+str(key)+"\", shape=none];")
        # self.addGraph("  }")

        if self.lastNode is not None:
            self.addGraph("  "+self.lastNode+" -> "+dummyHeadNode+" ;")
        self.lastNode = dummyHeadNode

        i = 0
        for key in curScope.LocalDict:
            self.lastNode = nodeList[i]
            i += 1
            # nodeList.remove(nodeList[0])
            curScope.LocalDict.get(key).accept(self, idx+2, True)


    def Graph_Visit_Field(self, curField, idx):
        tmpNode = ""
        if self.str_obj_dict.has_key(curField.toString()) is True:
            tmpNode = self.str_obj_dict[curField.toString()]
            
        else:
            tmpNode = self.nextNode()
            self.str_obj_dict[curField.toString()] = tmpNode
            self.addGraph("    "+tmpNode+" [label=\"\", shape=circle];")

        self.addGraph("  "+self.lastNode+" -> "+tmpNode+" ;")
        self.lastNode = tmpNode

        curField.typePtr.accept(self, idx+2, True)


    def Graph_Visit_Record(self, curRecord, idx):
        tmpNode = ""
        if self.str_obj_dict.has_key(curRecord.toString()) is True:
            tmpNode = self.str_obj_dict[curRecord.toString()]
            
        else:
            tmpNode = self.nextNode()
            self.str_obj_dict[curRecord.toString()] = tmpNode
            self.addGraph("    "+tmpNode+" [label=\"Record\", style=rounded, shape=rectangle];")
        
        self.addGraph("  "+self.lastNode+" -> "+tmpNode+" ;")
        self.lastNode = tmpNode

        curRecord.scopePtr.accept(self, idx+1, True)


    def Graph_Visit_Array(self, curArray, idx):
        length = str(curArray.length.val)
        tmpNode = ""
        if self.str_obj_dict.has_key(curArray.toString()) is True:
            tmpNode = self.str_obj_dict[curArray.toString()]
            
        else:
            tmpNode = self.nextNode()
            self.str_obj_dict[curArray.toString()] = tmpNode
            self.addGraph("    "+tmpNode+" [label=\"Array\\n"+length+"\", style=rounded, shape=rectangle];")

        self.addGraph("  "+self.lastNode+" -> "+tmpNode+" ;")
        self.lastNode = tmpNode

        curArray.typePtr.accept(self, idx+2, True)


    def Graph_Visit_Integer(self, curInteger, idx):
        if self.integer_node is False:
            self.addGraph("    "+"N_INT"+" [label=\"Integer\", style=rounded, shape=rectangle];")
            self.integer_node = True
        self.addGraph("  "+self.lastNode+" -> "+"N_INT"+" ;")
        self.lastNode = "N_INT"


    def Graph_Visit_Variable(self, curVariable, idx):
        tmpNode = ""
        if self.str_obj_dict.has_key(curVariable.toString()) is True:
            tmpNode = self.str_obj_dict[curVariable.toString()]
            
        else:
            tmpNode = self.nextNode()
            self.str_obj_dict[curVariable.toString()] = tmpNode
            self.addGraph("    "+tmpNode+" [label=\"\", shape=circle];")

        self.addGraph("  "+self.lastNode+" -> "+tmpNode+" ;")
        self.lastNode = tmpNode

        curVariable.typePtr.accept(self, idx+2, True)


    def Graph_Visit_Constant(self, curConstant, idx):
        num = str(curConstant.val)
        tmpNode = ""
        if self.str_obj_dict.has_key(curConstant.toString()) is True:
            tmpNode = self.str_obj_dict[curConstant.toString()]
            
        else:
            tmpNode = self.nextNode()
            self.str_obj_dict[curConstant.toString()] = tmpNode
            self.addGraph("    "+tmpNode+" [label=\""+num+"\", shape=diamond];")

        self.addGraph("  "+self.lastNode+" -> "+tmpNode+" ;")
        self.lastNode = tmpNode

        curConstant.typePtr.accept(self, idx+2, True)

# AST Visitor method

    def Visit_AST_Variable(self, astVariable, idx):
        self.addContent("  "*idx+"Variable:")
        self.addContent("  "*idx+"variable =>")
        astVariable.ST.accept(self, idx+1, False)


    def Visit_AST_Index(self, astIndex, idx):
        self.addContent("  "*idx+"Index:")
        self.addContent("  "*idx+"location =>")
        astIndex.location.accept(self, idx+1, False)
        self.addContent("  "*idx+"expression =>")
        astIndex.expression.accept(self, idx+1, False)


    def Visit_AST_Field(self, astField, idx):
        self.addContent("  "*idx+"Field:")
        self.addContent("  "*idx+"location =>")
        astField.location.accept(self, idx+1, False)
        self.addContent("  "*idx+"variable =>")
        astField.variable.accept(self, idx+1, False)


    def Visit_AST_Number(self, astNumber, idx):
        self.addContent("  "*idx+"Number:")
        self.addContent("  "*idx+"value =>")
        astNumber.ST.accept(self, idx+1, False)


    def Visit_AST_Binary(self, astBinary, idx):
        self.addContent("  "*idx+"Binary ("+str(astBinary.op)+"):")
        self.addContent("  "*idx+"left =>")
        astBinary.left.accept(self, idx+1, False)
        self.addContent("  "*idx+"right =>")
        astBinary.right.accept(self, idx+1, False)


    def Visit_AST_Condition(self, astCondition, idx):
        self.addContent("  "*idx+"Condition ("+str(astCondition.op)+"):")
        self.addContent("  "*idx+"left =>")
        astCondition.left.accept(self, idx+1, False)
        self.addContent("  "*idx+"right =>")
        astCondition.right.accept(self, idx+1, False)


    def Visit_AST_Assign(self, astAssign, idx):
        self.addContent("  "*idx+"Assign:")
        self.addContent("  "*idx+"location =>")
        astAssign.location.accept(self, idx+1, False)
        self.addContent("  "*idx+"expression =>")
        astAssign.expression.accept(self, idx+1, False)

        if astAssign.nextInst is not None:
            astAssign.nextInst.accept(self, idx, False)


    def Visit_AST_Read(self, astRead, idx):
        self.addContent("  "*idx+"Read:")
        self.addContent("  "*idx+"location =>")
        astRead.location.accept(self, idx+1, False)

        if astRead.nextInst is not None:
            astRead.nextInst.accept(self, idx, False)


    def Visit_AST_Write(self, astWrite, idx):
        self.addContent("  "*idx+"Write:")
        self.addContent("  "*idx+"expression =>")
        astWrite.expression.accept(self, idx+1, False)

        if astWrite.nextInst is not None:
            astWrite.nextInst.accept(self, idx, False)


    def Visit_AST_If(self, astIf, idx):
        self.addContent("  "*idx+"If:")
        self.addContent("  "*idx+"condition =>")
        astIf.cond.accept(self, idx+1, False)
        self.addContent("  "*idx+"true =>")
        astIf.true_Inst.accept(self, idx+1, False)
        if astIf.false_Inst is not None:
            self.addContent("  "*idx+"false =>")
            astIf.false_Inst.accept(self, idx+1, False)

        if astIf.nextInst is not None:
            astIf.nextInst.accept(self, idx, False)


    def Visit_AST_Repeat(self, astRepeat, idx):
        self.addContent("  "*idx+"Repeat:")
        self.addContent("  "*idx+"condition =>")
        astRepeat.cond.accept(self, idx+1, False)
        self.addContent("  "*idx+"instructions =>")
        astRepeat.inst.accept(self, idx+1, False)
        
        if astRepeat.nextInst is not None:
            astRepeat.nextInst.accept(self, idx, False)


# AST Graphic 



    def Graph_Visit_AST_Variable(self, astVariable, idx):
        tmpNode = self.nextNode()
        self.addGraph("    "+tmpNode+" [label=\"Variable\", shape=box];")
        if self.ast_sk.isEmpty() == False:
            skTop = self.ast_sk.peek()
            self.addGraph("  "+str(skTop[0])+" -> "+tmpNode+" [label="+str(skTop[1])+"];")
        
        StNode = self.nextNode()
        self.addGraph("    "+StNode+" [label=\""+str(astVariable.Id)+"\", shape=circle];")
        self.addGraph("  "+tmpNode+" -> "+StNode+" [label=ST];")


    def Graph_Visit_AST_Index(self, astIndex, idx):
        tmpNode = self.nextNode()
        self.addGraph("    "+tmpNode+" [label=\"Index\", shape=box];")
        if self.ast_sk.isEmpty() == False:
            skTop = self.ast_sk.peek()
            self.addGraph("  "+str(skTop[0])+" -> "+tmpNode+" [label="+str(skTop[1])+"];")
        pushList = []
        pushList.append(tmpNode)
        pushList.append("location")
        self.ast_sk.push(pushList)
        astIndex.location.accept(self, idx+1, True)
        self.ast_sk.pop()

        pushList = []
        pushList.append(tmpNode)
        pushList.append("expression")
        self.ast_sk.push(pushList)
        astIndex.expression.accept(self, idx+1, True)
        self.ast_sk.pop()


    def Graph_Visit_AST_Field(self, astField, idx):
        tmpNode = self.nextNode()
        self.addGraph("    "+tmpNode+" [label=\"Field\", shape=box];")
        if self.ast_sk.isEmpty() == False:
            skTop = self.ast_sk.peek()
            self.addGraph("  "+str(skTop[0])+" -> "+tmpNode+" [label="+str(skTop[1])+"];")
        pushList = []
        pushList.append(tmpNode)
        pushList.append("location")
        self.ast_sk.push(pushList)
        astField.location.accept(self, idx+1, True)
        self.ast_sk.pop()

        pushList = []
        pushList.append(tmpNode)
        pushList.append("variable")
        self.ast_sk.push(pushList)
        astField.variable.accept(self, idx+1, True)
        self.ast_sk.pop()


    def Graph_Visit_AST_Number(self, astNumber, idx):
        tmpNode = self.nextNode()
        self.addGraph("    "+tmpNode+" [label=\"Number\", shape=box];")
        if self.ast_sk.isEmpty() == False:
            skTop = self.ast_sk.peek()
            self.addGraph("  "+str(skTop[0])+" -> "+tmpNode+" [label="+str(skTop[1])+"];")
        
        StNode = self.nextNode()
        self.addGraph("    "+StNode+" [label=\""+str(astNumber.val)+"\", shape=diamond];")
        self.addGraph("  "+tmpNode+" -> "+StNode+" [label=ST];")


    def Graph_Visit_AST_Binary(self, astBinary, idx):
        tmpNode = self.nextNode()
        self.addGraph("    "+tmpNode+" [label=\""+str(astBinary.op)+"\", shape=box];")
        if self.ast_sk.isEmpty() == False:
            skTop = self.ast_sk.peek()
            self.addGraph("  "+str(skTop[0])+" -> "+tmpNode+" [label="+str(skTop[1])+"];")
        pushList = []
        pushList.append(tmpNode)
        pushList.append("left")
        self.ast_sk.push(pushList)
        astBinary.left.accept(self, idx+1, True)
        self.ast_sk.pop()

        pushList = []
        pushList.append(tmpNode)
        pushList.append("right")
        self.ast_sk.push(pushList)
        astBinary.right.accept(self, idx+1, True)
        self.ast_sk.pop()


    def Graph_Visit_AST_Condition(self, astCondition, idx):
        tmpNode = self.nextNode()
        self.addGraph("    "+tmpNode+" [label=\""+str(astCondition.op)+"\", shape=box];")
        if self.ast_sk.isEmpty() == False:
            skTop = self.ast_sk.peek()
            self.addGraph("  "+str(skTop[0])+" -> "+tmpNode+" [label="+str(skTop[1])+"];")
        pushList = []
        pushList.append(tmpNode)
        pushList.append("left")
        self.ast_sk.push(pushList)
        astCondition.left.accept(self, idx+1, True)
        self.ast_sk.pop()

        pushList = []
        pushList.append(tmpNode)
        pushList.append("right")
        self.ast_sk.push(pushList)
        astCondition.right.accept(self, idx+1, True)
        self.ast_sk.pop()


    def Graph_Visit_AST_Assign(self, astAssign, idx):
        tmpNode = self.nextNode()
        self.addGraph("    "+tmpNode+" [label=\":=\", shape=box];")
        if self.ast_sk.isEmpty() == False:
            skTop = self.ast_sk.peek()
            self.addGraph("  "+str(skTop[0])+" -> "+tmpNode+" [label="+str(skTop[1])+"];")
        pushList = []
        pushList.append(tmpNode)
        pushList.append("location")
        self.ast_sk.push(pushList)
        astAssign.location.accept(self, idx+1, True)
        self.ast_sk.pop()

        pushList = []
        pushList.append(tmpNode)
        pushList.append("expression")
        self.ast_sk.push(pushList)
        astAssign.expression.accept(self, idx+1, True)
        self.ast_sk.pop()

        if astAssign.nextInst is not None:
            pushList = []
            pushList.append(tmpNode)
            pushList.append("next")
            self.ast_sk.push(pushList)
            astAssign.nextInst.accept(self, idx+1, True)
            self.ast_sk.pop()


    def Graph_Visit_AST_Read(self, astRead, idx):
        tmpNode = self.nextNode()
        self.addGraph("    "+tmpNode+" [label=\"Read\", shape=box];")
        if self.ast_sk.isEmpty() == False:
            skTop = self.ast_sk.peek()
            self.addGraph("  "+str(skTop[0])+" -> "+tmpNode+" [label="+str(skTop[1])+"];")
        pushList = []
        pushList.append(tmpNode)
        pushList.append("location")
        self.ast_sk.push(pushList)
        astRead.location.accept(self, idx+1, True)
        self.ast_sk.pop()

        if astRead.nextInst is not None:
            pushList = []
            pushList.append(tmpNode)
            pushList.append("next")
            self.ast_sk.push(pushList)
            astRead.nextInst.accept(self, idx+1, True)
            self.ast_sk.pop()


    def Graph_Visit_AST_Write(self, astWrite, idx):
        tmpNode = self.nextNode()
        self.addGraph("    "+tmpNode+" [label=\"Write\", shape=box];")
        if self.ast_sk.isEmpty() == False:
            skTop = self.ast_sk.peek()
            self.addGraph("  "+str(skTop[0])+" -> "+tmpNode+" [label="+str(skTop[1])+"];")
        pushList = []
        pushList.append(tmpNode)
        pushList.append("expression")
        self.ast_sk.push(pushList)
        astWrite.expression.accept(self, idx+1, True)
        self.ast_sk.pop()

        if astWrite.nextInst is not None:
            pushList = []
            pushList.append(tmpNode)
            pushList.append("next")
            self.ast_sk.push(pushList)
            astWrite.nextInst.accept(self, idx+1, True)
            self.ast_sk.pop()


    def Graph_Visit_AST_If(self, astIf, idx):
        tmpNode = self.nextNode()
        self.addGraph("    "+tmpNode+" [label=\"If\", shape=box];")
        if self.ast_sk.isEmpty() == False:
            skTop = self.ast_sk.peek()
            self.addGraph("  "+str(skTop[0])+" -> "+tmpNode+" [label="+str(skTop[1])+"];")
        pushList = []
        pushList.append(tmpNode)
        pushList.append("condition")
        self.ast_sk.push(pushList)
        astIf.cond.accept(self, idx+1, True)
        self.ast_sk.pop()

        pushList = []
        pushList.append(tmpNode)
        pushList.append("true")
        self.ast_sk.push(pushList)
        astIf.true_Inst.accept(self, idx+1, True)
        self.ast_sk.pop()

        if astIf.false_Inst is not None:
            pushList = []
            pushList.append(tmpNode)
            pushList.append("false")
            self.ast_sk.push(pushList)
            astIf.false_Inst.accept(self, idx+1, True)
            self.ast_sk.pop()

        if astIf.nextInst is not None:
            pushList = []
            pushList.append(tmpNode)
            pushList.append("next")
            self.ast_sk.push(pushList)
            astIf.nextInst.accept(self, idx+1, True)
            self.ast_sk.pop()


    def Graph_Visit_AST_Repeat(self, astRepeat, idx):
        tmpNode = self.nextNode()
        self.addGraph("    "+tmpNode+" [label=\"Repeat\", shape=box];")
        if self.ast_sk.isEmpty() == False:
            skTop = self.ast_sk.peek()
            self.addGraph("  "+str(skTop[0])+" -> "+tmpNode+" [label="+str(skTop[1])+"];")
        pushList = []
        pushList.append(tmpNode)
        pushList.append("condition")
        self.ast_sk.push(pushList)
        astRepeat.cond.accept(self, idx+1, True)
        self.ast_sk.pop()

        pushList = []
        pushList.append(tmpNode)
        pushList.append("instructions")
        self.ast_sk.push(pushList)
        astRepeat.inst.accept(self, idx+1, True)
        self.ast_sk.pop()

        if astRepeat.nextInst is not None:
            pushList = []
            pushList.append(tmpNode)
            pushList.append("next")
            self.ast_sk.push(pushList)
            astRepeat.nextInst.accept(self, idx+1, True)
            self.ast_sk.pop()
