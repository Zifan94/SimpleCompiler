# Zifan Yang
# zyang45@jhu.edu

class Stack(object):
	elements = []

	def __init__(self):
		self.elements = []

	def isEmpty(self):
		return len(self.elements) == 0

	def peek(self):
		return self.elements[self.size()-1]

	def size(self):
		return len(self.elements)

	def push(self, obj):
		# print("PUSH: "+str(obj))
		self.elements.append(obj)

	def pop(self):
		# print("POP: "+str(self.elements[self.size()-1]))
		return self.elements.pop()


# print("test stack")
# sk = Stack()
# sk.push(11)
# mylist = []
# mylist.append('a')
# mylist.append('b')
# sk.push(mylist)
# print(sk.pop())
# print(sk.pop())