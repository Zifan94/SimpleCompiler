# Zifan Yang
# zyang45@jhu.edu

from Global import *
from MyException import *

class Token():
	Type = "" # "keyword", "identifier", "integer", "eof"
	Value_Str = "" 	   # store the origin string
	Value_Int = 0      # only valid when Type = "integer"
	startPos = -1	   # start position in source file
	endPos = -1		   # end position in source file


	def __init__(self, inputStr, Type, firstPos, lastPos):
		self.Value_Str = inputStr
		self.startPos = firstPos
		self.endPos = lastPos

		if Type == "keyword":
			self.Type = "keyword"

		elif Type == "identifier":
			self.Type = "identifier"

		elif Type == "integer":
			self.Type = "integer"
			self.Value_Int = int(inputStr)

		elif Type == "eof":
			self.Type = "eof"

		else:
			ErrMsg = "cannot create a Token with unknown Type: "+Type
			raise TokenException(ErrMsg)


	def getDescription(self):
		description = ""
		if self.Type == "keyword":

			description += self.Value_Str
			description += "@"
			description += "("+str(self.startPos)+", "+str(self.endPos)+")"

		elif self.Type == "identifier":

			description += "identifier"
			description += "<"+self.Value_Str+">"
			description += "@"
			description += "("+str(self.startPos)+", "+str(self.endPos)+")"

		elif self.Type == "integer":

			description += "integer"
			description += "<"+self.Value_Str+">"
			description += "@"
			description += "("+str(self.startPos)+", "+str(self.endPos)+")"

		elif self.Type == "eof":

			description += "eof"
			description += "@"
			description += "("+str(self.startPos)+", "+str(self.endPos)+")"

		else:
			return "Type error in getDescription()"

		return description

