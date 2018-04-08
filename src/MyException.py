# Zifan Yang
# zyang45@jhu.edu

ERRORHEADER = "error: "
class BaseException(Exception):
	errorInfo = ""
	def __init__(self, err):
		Exception.__init__(self, err)
		self.errorInfo = err

	def __str__(self):
		return self.errorInfo

	def add(self, err):
		self.errorInfo += '\n'+err

class DriverException(BaseException):
	errorInfo = ""
	def __init__(self, err):
		BaseException.__init__(self, err)
		self.errorInfo = ERRORHEADER+err

	def __str__(self):
		return self.errorInfo

	def add(self, err):
		self.errorInfo += '\n'+ERRORHEADER+err

class ScannerException(BaseException):
	errorInfo = ""
	def __init__(self, err):
		BaseException.__init__(self, err)
		self.errorInfo = ERRORHEADER+err

	def __str__(self):
		return self.errorInfo

	def add(self, err):
		self.errorInfo += '\n'+ERRORHEADER+err

class TokenException(BaseException):
	errorInfo = ""
	def __init__(self, err):
		BaseException.__init__(self, err)
		self.errorInfo = ERRORHEADER+err

	def __str__(self):
		return self.errorInfo

	def add(self, err):
		self.errorInfo += '\n'+ERRORHEADER+err

class ParserException(BaseException):
	errorInfo = ""
	def __init__(self, err):
		BaseException.__init__(self, err)
		self.errorInfo = err

	def __str__(self):
		return self.errorInfo

	def add(self, err):
		self.errorInfo += '\n'+ERRORHEADER+err
