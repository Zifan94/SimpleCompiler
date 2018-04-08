# Zifan Yang
# zyang45@jhu.edu

from MyException import *

class GlobalVal():
	ERRORHEADER = "error: "
	KEYWORD = ["PROGRAM", "BEGIN", "END", "CONST", "TYPE", "VAR", "ARRAY", "OF", "RECORD", "IF", 
				"THEN", "ELSE", "REPEAT", "UNTIL", "WHILE", "DO", "WRITE", "READ", "DIV", "MOD"]
	DIGIT = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
	LETTER = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y" ,"z",
		"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
	SKIP = [" ", "	", "\n", "\r"]
	DELIMITER = [";", ".", "=", ":", "+", "-", "*", "(", ")", ":=", "#", "<", ">",
				"<=", ">=", "[", "]", ","]
	DOUBLE_DELIMITER = [":=", "<=", ">="]
	COMMENT = ["(*", "*)"]

	# @staticmethod
	# def ERROR_HANDLER(errClass, errMsg):
	# 	# raise ParserException(errMsg)
	# 	print(errMsg)