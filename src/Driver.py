# Zifan Yang
# zyang45@jhu.edu

import sys
from Token import *
from Scanner import *
from Parser import *
from Global import *
from MyException import *
from Observer import *
from ErrorHandler import *
from Visitor import *
from Interpreter import *
from CodeGen import *

if __name__ == "__main__":

	try:	
		argvLen = len(sys.argv)
		arg1 = ""
		arg2 = ""
		arg3 = ""

		### arguments checking ###
		if argvLen == 1:
			pass
			# ErrMsg = "there should be at least one arguments"
			# raise DriverException(ErrMsg)

		elif argvLen == 2:
			arg1 = sys.argv[1]
		elif argvLen == 3:
			arg1 = sys.argv[1]
			arg2 = sys.argv[2]
		elif argvLen == 4:
			arg1 = sys.argv[1]
			arg2 = sys.argv[2]
			arg3 = sys.argv[3]
		else:
			ErrMsg = "there are more then three arguments"
			raise DriverException(ErrMsg)

		### check option ###	
		if arg1 == "-s": ######################### Assignment 1 ###################
			if arg2 == "": # read from terminal                      ./sc -s
				inputSourceStr = sys.stdin.readline()
				MyScanner = Scanner(inputSourceStr)
				tokenList = MyScanner.all()
		
			elif arg3 == "": # read from file specified by arg2      ./sc -s filename
				with open(arg2,'r') as f:
					inputSourceStr = f.read()
				MyScanner = Scanner(inputSourceStr)
				tokenList = MyScanner.all()

			else:
				ErrMsg = "-c wont support three arguments"
				raise DriverException(ErrMsg)

		elif arg1 == "-c":######################### Assignment 2 ################
			if arg2 == "": # read from terminal     				  ./sc -c
				inputSourceStr = sys.stdin.readline()
				MyErrHandler = ErrorHandeler(inputSourceStr)
				MyScanner = Scanner(inputSourceStr)
				tokenList = MyScanner.all(isLog = False)
				MyErrHandler.add_tokenList(tokenList)

				MyParser = Parser(tokenList, MyErrHandler)
				ob = TextObserver()
				MyParser.attach(ob)
				MyParser.parse()
				# MyErrHandler.show_err()
				ob.show()


			elif arg3 == "": # read from file specified by arg2  
				if arg2 == "-g":#										./sc -c -g
					inputSourceStr = sys.stdin.readline()
					MyErrHandler = ErrorHandeler(inputSourceStr)
					MyScanner = Scanner(inputSourceStr)
					tokenList = MyScanner.all(isLog = False)
					MyErrHandler.add_tokenList(tokenList)

					MyParser = Parser(tokenList, MyErrHandler)
					ob = GraphicObserver()
					MyParser.attach(ob)
					MyParser.parse()
					# MyErrHandler.show_err()
					ob.show()
				else:#													./sc  -c  filename
					with open(arg2,'r') as f:
						inputSourceStr = f.read()
					MyErrHandler = ErrorHandeler(inputSourceStr)
					MyScanner = Scanner(inputSourceStr)
					tokenList = MyScanner.all(isLog = False)
					MyErrHandler.add_tokenList(tokenList)

					MyParser = Parser(tokenList, MyErrHandler)
					ob = TextObserver()
					MyParser.attach(ob)
					MyParser.parse()
					# MyErrHandler.show_err()
					ob.show()

			elif arg2 == "-g":#											./sc -c -g filename
				with open(arg3,'r') as f:
						inputSourceStr = f.read()
				MyErrHandler = ErrorHandeler(inputSourceStr)
				MyScanner = Scanner(inputSourceStr)
				tokenList = MyScanner.all(isLog = False)
				MyErrHandler.add_tokenList(tokenList)

				MyParser = Parser(tokenList, MyErrHandler)
				ob = GraphicObserver()
				MyParser.attach(ob)
				MyParser.parse()
				# MyErrHandler.show_err()
				ob.show()

		elif arg1 == "-t": ######################### Assignment 3 ###################
			if arg2 == "": # read from terminal     				  ./sc -t
				inputSourceStr = sys.stdin.readline()
				MyErrHandler = ErrorHandeler(inputSourceStr)
				MyScanner = Scanner(inputSourceStr)
				tokenList = MyScanner.all(isLog = False)
				MyErrHandler.add_tokenList(tokenList)

				MyParser = Parser(tokenList, MyErrHandler)
				vt = Visitor()
				MyParser.attach_visitor(vt)
				MyParser.parse(isGraph=False)
				# MyErrHandler.show_err()
				print(vt.show_content())


			elif arg3 == "": # read from file specified by arg2  
				if arg2 == "-g":#										./sc -t -g
					inputSourceStr = sys.stdin.readline()
					MyErrHandler = ErrorHandeler(inputSourceStr)
					MyScanner = Scanner(inputSourceStr)
					tokenList = MyScanner.all(isLog = False)
					MyErrHandler.add_tokenList(tokenList)

					MyParser = Parser(tokenList, MyErrHandler)
					vt = Visitor()
					MyParser.attach_visitor(vt)
					MyParser.parse(isGraph=True)
					# MyErrHandler.show_err()
					print(vt.show_graph())
				else:#													./sc  -t  filename
					with open(arg2,'r') as f:
						inputSourceStr = f.read()
					MyErrHandler = ErrorHandeler(inputSourceStr)
					MyScanner = Scanner(inputSourceStr)
					tokenList = MyScanner.all(isLog = False)
					MyErrHandler.add_tokenList(tokenList)

					MyParser = Parser(tokenList, MyErrHandler)
					vt = Visitor()
					MyParser.attach_visitor(vt)
					MyParser.parse(isGraph=False)
					# MyErrHandler.show_err()
					print(vt.show_content())

			elif arg2 == "-g":#											./sc -t -g filename
				with open(arg3,'r') as f:
					inputSourceStr = f.read()
				MyErrHandler = ErrorHandeler(inputSourceStr)
				MyScanner = Scanner(inputSourceStr)
				tokenList = MyScanner.all(isLog = False)
				MyErrHandler.add_tokenList(tokenList)

				MyParser = Parser(tokenList, MyErrHandler)
				vt = Visitor()
				MyParser.attach_visitor(vt)
				MyParser.parse(isGraph=True)
				# MyErrHandler.show_err()
				print(vt.show_graph())
				

		elif arg1 == "-a": ######################### Assignment 4 ###################
			if arg2 == "": # read from terminal     				  ./sc -a
				inputSourceStr = sys.stdin.readline()
				MyErrHandler = ErrorHandeler(inputSourceStr)
				MyScanner = Scanner(inputSourceStr)
				tokenList = MyScanner.all(isLog = False)
				MyErrHandler.add_tokenList(tokenList)

				MyParser = Parser(tokenList, MyErrHandler)
				vt = Visitor()
				MyParser.attach_ast_visitor(vt)
				MyParser.parse(isGraph=False)
				# MyErrHandler.show_err()
				print(vt.show_content())


			elif arg3 == "": # read from file specified by arg2  
				if arg2 == "-g":#										./sc -a -g
					inputSourceStr = sys.stdin.readline()
					MyErrHandler = ErrorHandeler(inputSourceStr)
					MyScanner = Scanner(inputSourceStr)
					tokenList = MyScanner.all(isLog = False)
					MyErrHandler.add_tokenList(tokenList)

					MyParser = Parser(tokenList, MyErrHandler)
					vt = Visitor()
					MyParser.attach_ast_visitor(vt)
					MyParser.parse(isGraph=True)
					# MyErrHandler.show_err()
					print(vt.show_graph())
				else:#													./sc  -a  filename
					with open(arg2,'r') as f:
						inputSourceStr = f.read()
					MyErrHandler = ErrorHandeler(inputSourceStr)
					MyScanner = Scanner(inputSourceStr)
					tokenList = MyScanner.all(isLog = False)
					MyErrHandler.add_tokenList(tokenList)

					MyParser = Parser(tokenList, MyErrHandler)
					vt = Visitor()
					MyParser.attach_ast_visitor(vt)
					MyParser.parse(isGraph=False)
					# MyErrHandler.show_err()
					print(vt.show_content())

			elif arg2 == "-g":#											./sc -a -g filename
				with open(arg3,'r') as f:
					inputSourceStr = f.read()
				MyErrHandler = ErrorHandeler(inputSourceStr)
				MyScanner = Scanner(inputSourceStr)
				tokenList = MyScanner.all(isLog = False)
				MyErrHandler.add_tokenList(tokenList)

				MyParser = Parser(tokenList, MyErrHandler)
				vt = Visitor()
				MyParser.attach_ast_visitor(vt)
				MyParser.parse(isGraph=True)
				# MyErrHandler.show_err()
				print(vt.show_graph())

		elif arg1 == "-i": ######################### Assignment 5 ###################
			if arg2 == "": # read from terminal                      ./sc -i
				inputSourceStr = sys.stdin.readline()
				MyErrHandler = ErrorHandeler(inputSourceStr)
				MyScanner = Scanner(inputSourceStr)
				tokenList = MyScanner.all(isLog = False)
				MyErrHandler.add_tokenList(tokenList)

				MyParser = Parser(tokenList, MyErrHandler)
				vt = Visitor()
				MyParser.attach_ast_visitor(vt)
				Program_Scope, AST_root = MyParser.parse(isGraph=False)
				# print(vt.show_content())

				MyInterpreter = Interpreter(Program_Scope, AST_root, MyErrHandler)
				MyInterpreter.interpret()
		
			elif arg3 == "": # read from file specified by arg2      ./sc -i filename
				with open(arg2,'r') as f:
					inputSourceStr = f.read()
				MyErrHandler = ErrorHandeler(inputSourceStr)
				MyScanner = Scanner(inputSourceStr)
				tokenList = MyScanner.all(isLog = False)
				MyErrHandler.add_tokenList(tokenList)

				MyParser = Parser(tokenList, MyErrHandler)
				vt = Visitor()
				MyParser.attach_ast_visitor(vt)
				Program_Scope, AST_root = MyParser.parse(isGraph=False)
				# print(vt.show_content())

				MyInterpreter = Interpreter(Program_Scope, AST_root, MyErrHandler)
				MyInterpreter.interpret()

			else:
				ErrMsg = "-c wont support three arguments"
				raise DriverException(ErrMsg)

		######################### Assignment 6 ###################
		elif arg1 == "": # ./sc
			inputSourceStr = sys.stdin.readline()
			MyErrHandler = ErrorHandeler(inputSourceStr)
			MyScanner = Scanner(inputSourceStr)
			tokenList = MyScanner.all(isLog = False)
			MyErrHandler.add_tokenList(tokenList)

			MyParser = Parser(tokenList, MyErrHandler)
			vt = Visitor()
			MyParser.attach_ast_visitor(vt)
			Program_Scope, AST_root = MyParser.parse(isGraph=False)
			# print(vt.show_content())

			# MyInterpreter = Interpreter(Program_Scope, AST_root, MyErrHandler)
			# MyInterpreter.interpret()
			MyCodeGen = CodeGen(Program_Scope, AST_root, MyErrHandler)
			MyCodeGen.generateCode()
		elif arg1 != "" and arg2 == "": # ./sc input.sim
			with open(arg1,'r') as f:
				inputSourceStr = f.read()
			MyErrHandler = ErrorHandeler(inputSourceStr)
			MyScanner = Scanner(inputSourceStr)
			tokenList = MyScanner.all(isLog = False)
			MyErrHandler.add_tokenList(tokenList)

			MyParser = Parser(tokenList, MyErrHandler)
			vt = Visitor()
			MyParser.attach_ast_visitor(vt)
			Program_Scope, AST_root = MyParser.parse(isGraph=False)
			# print(vt.show_content())

			# MyInterpreter = Interpreter(Program_Scope, AST_root, MyErrHandler)
			# MyInterpreter.interpret()
			MyCodeGen = CodeGen(Program_Scope, AST_root, MyErrHandler)
			MyCodeGen.generateCode(arg1)

		




		else:
			ErrMsg = "option currently not supported"
			raise DriverException(ErrMsg)

	except BaseException, error: 
		sys.stderr.write(error.errorInfo+"\n")
		sys.stderr.flush()
		sys.exit(1)
