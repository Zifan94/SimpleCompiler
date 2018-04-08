# Zifan Yang
# zyang45@jhu.edu
from Stack import *

class Observer():

	def start(self, production):
		pass

	def stop(self, production):
		pass

	def match(self, curToken):
		pass


class TextObserver(Observer):

	output = ""
	spaceCnt = 0

	def __init__(self):
		self.output = ""
		self.spaceCnt = 0

	def start(self, production):
		spaceStr = (self.spaceCnt) * " "
		self.output += spaceStr + production + '\n'
		self.spaceCnt += 2

	def stop(self, production):
		self.spaceCnt -= 2

	def match(self, curToken):
		spaceStr = (self.spaceCnt) * " "
		self.output += spaceStr + curToken.getDescription() +'\n'

	def show(self):
		print(self.output[:len(self.output)-1])


class GraphicObserver(Observer):

	output = ""
	sk = None
	label_sk = None
	NTCnt = 0
	TCnt = 0

	def __init__(self, name = "Parse_Tree_Graph"):
		self.output = "digraph "+name+" {\n"
		self.sk = Stack()
		self.label_sk = Stack()
		self.NTCnt = 0
		self.TCnt = 0

	def start(self, production):
		curNode = "NT_"+str(self.NTCnt)
		if self.sk.isEmpty() == True:
			self.output += "	" + curNode + " [label=\""+production+"\" ,shape=rectangle];\n"
			self.sk.push(production)
			self.label_sk.push(curNode)
		else:
			self.output += "	" + curNode + " [label=\""+production+"\" ,shape=rectangle];\n"
			self.output += "	" + self.label_sk.peek()+" -> "+curNode +';\n'
			self.sk.push(production)
			self.label_sk.push(curNode)
		self.NTCnt += 1

	def stop(self, production):
		if self.sk.isEmpty() == False:
			self.sk.pop()
			self.label_sk.pop()

	def match(self, curToken):
		tokenName = ""
		curNode = "T_"+str(self.TCnt)
		if curToken.Type == "keyword" or curToken.Type == "identifier":
			tokenName = curToken.Value_Str
		elif curToken.Type == "integer":
			tokenName = str(curToken.Value_Int)
		if self.sk.isEmpty() == False:
			self.output += "	" + curNode + " [label=\""+tokenName+"\" ,shape=diamond];\n"
			self.output += "	" + self.label_sk.peek()+" -> "+curNode +';\n'
		self.TCnt += 1
		
	def show(self):
		self.output += "} \n"
		print(self.output[:len(self.output)-1])