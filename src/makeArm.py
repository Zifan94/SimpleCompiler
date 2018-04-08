# Zifan Yang
# zyang45@jhu.edu

from os import environ, system
import os

def green(text):
	return "\033[1;32m{}\033[0;0m".format(text)

def red(text):
	return "\033[1;31m{}\033[0;0m".format(text)

def blue(text):
	return "\033[1;34m{}\033[0;0m".format(text)

def runTestCase(sim_file):
	state = "right"
	# sim_file = "test.sim"
	# ans_file = "test.scanner"
	subPro = run(["./sc", sim_file], stdin = DEVNULL, stdout = PIPE, stderr = PIPE)
	
	resList = subPro.stdout.decode()
	errStr = subPro.stderr.decode()
	print(red(" "+sim_file))
	if resList != "":
		print("  "+resList)
	if errStr != "":
		print("  "+errStr)

	return 1
	

if __name__ == "__main__":
	root = os.path.dirname(os.path.abspath("makeArm.py"))
	testCaseFolder = root+"/"
	print(testCaseFolder)
	caseList = os.listdir(testCaseFolder)
	simList = []
	cnt = 0
	for curFileName in caseList:
		if ".s" in curFileName:
			outFileName = curFileName[:-2]
			print(red(outFileName))
			system("gcc -o "+outFileName+" "+curFileName)
			cnt += 1

	print("==================================")
	print(blue(str(cnt)+" files processed!\n"))


