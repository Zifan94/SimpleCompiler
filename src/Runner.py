# Zifan Yang
# zyang45@jhu.edu

from os import environ, system
import os
from subprocess import PIPE, run, Popen, DEVNULL

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
	root = os.path.dirname(os.path.abspath("Runner.py"))
	testCaseFolder = root+"/CodeGen_test_case/"
	print(testCaseFolder)
	caseList = os.listdir(testCaseFolder)
	simList = []
	cnt = 0
	for curFileName in caseList:
		if ".sim" in curFileName:
			cnt += runTestCase("CodeGen_test_case/"+curFileName)

	print("==================================")
	print(blue(str(cnt)+" files processed!\n"))

	print(blue("moving to CodeGen_test_case/ARM..."))
	system("mv CodeGen_test_case/*.s CodeGen_test_case/ARM")
	print(blue("move completed!"))

