# Zifan Yang
# zyang45@jhu.edu

from Global import GlobalVal
from Token import Token
from Stack import Stack
from MyException import ScannerException


class Scanner():

    sourceText = ""
    nextPos = 0
    totalLen = -1
    TokenList = []
    isCommentStack = None
    getUnaccepableStr = -1

    def __init__(self, sourceText):
        sourceText += " "
        self.sourceText = sourceText
        self.nextPos = 0
        self.totalLen = len(self.sourceText)-1
        self.TokenList = []
        self.isCommentStack = Stack()
        self.getUnaccepableStr = -1

    def next(self):
        if self.getUnaccepableStr >= 0:  # previous next detected an error
            ErrMsg = "can not accept from \""
            ErrMsg += self.sourceText[self.getUnaccepableStr]
            ErrMsg += "\" @("+str(self.getUnaccepableStr)+", "
            ErrMsg += str(self.getUnaccepableStr)+")"
            raise ScannerException(ErrMsg)

        # reach the end of source file which is the space we added manually
        if self.nextPos == self.totalLen:
            newToken = Token("eof", "eof", self.nextPos, self.nextPos)
            self.nextPos += 1
            return newToken

        if self.nextPos > self.totalLen:  # next() is called after eof returned
            ErrMsg = "cannot call next() after whole source has been processed"
            raise ScannerException(ErrMsg)

        startPos = self.nextPos
        nextPos = self.nextPos
        endPos = self.nextPos
        reachFirstChar = False

        resultStr = ""
        while nextPos < self.totalLen:
            curChar = self.sourceText[nextPos]
            if reachFirstChar is False and curChar in GlobalVal.SKIP:
                startPos += 1
                nextPos += 1
                endPos += 1
                continue

            # now curChar is the first char that make sense.
            if reachFirstChar is False:
                reachFirstChar = True
                if curChar in GlobalVal.DELIMITER:  # DELIMITER
                    nextChar = self.sourceText[nextPos+1]
                    curChar_nextChar = curChar + nextChar
                    if curChar_nextChar in GlobalVal.DOUBLE_DELIMITER:  # :=, <=, >=
                        resultStr += curChar_nextChar
                        endPos = nextPos+1
                        nextPos += 2
                        break
                    elif curChar_nextChar in GlobalVal.COMMENT:  # (*, *)
                        if curChar_nextChar == "(*":
                            self.isCommentStack.push(nextPos)
                            resultStr += curChar_nextChar
                            endPos = nextPos+1
                            nextPos += 2
                            break
                        elif curChar_nextChar == "*)":
                            if self.isCommentStack.isEmpty() is False:
                                self.isCommentStack.pop()
                                resultStr += curChar_nextChar
                                endPos = nextPos+1
                                nextPos += 2
                                break
                            # found a "*)" but no "(*" before, just read in * and ) normally
                            else:
                                resultStr += curChar
                                endPos = nextPos
                                nextPos += 1
                                break

                    else:  # normal Delimiter
                        resultStr += curChar
                        endPos = nextPos
                        nextPos += 1
                        break
                else:  # normal LETTER or DIGIT
                    resultStr += curChar
                    endPos = nextPos
                    nextPos += 1
                    continue

            if reachFirstChar is True:
                if curChar in GlobalVal.SKIP:  # SKIP at end, end scan
                    break

                elif curChar in GlobalVal.DELIMITER:  # DELIMITER at end, end scan
                    break

                else:  # normal LETTER or DIGIT, processing
                    resultStr += curChar
                    endPos = nextPos
                    nextPos += 1
                    continue

        # while end here
        if resultStr in GlobalVal.COMMENT or self.isCommentStack.isEmpty() is False:
            self.nextPos = nextPos
            # return None
            return self.next()

        if resultStr == "" and nextPos >= self.totalLen:  # reach the end of source file
            self.nextPos = nextPos
            # return None
            return self.next()

        self.nextPos = nextPos
        Type = self.getType(resultStr)

        if Type == "bad input":
            lastPos = len(resultStr)
            while lastPos > 0:
                tmpStr = resultStr[0:lastPos]
                tmpType = self.getType(tmpStr)
                if tmpType == "bad input":
                    lastPos = lastPos-1
                    continue
                else:
                    self.nextPos = nextPos - (len(resultStr) - lastPos)
                    newToken = Token(tmpStr, tmpType, startPos, startPos+lastPos-1)
                    self.getUnaccepableStr = self.nextPos
                    return newToken

            ErrMsg = "Scanner cannot accept \""+resultStr+"\" @("+str(startPos)+", "+str(endPos)+")"
            raise ScannerException(ErrMsg)

        newToken = Token(resultStr, Type, startPos, endPos)
        if newToken is None:
            return self.next()
        else:
            return newToken

    def all(self, isLog=True):
        if self.nextPos != 0:
            ErrMsg = "Scanner cannot call all() because next() is already called somewhere"
            raise ScannerException(ErrMsg)
        curToken = None
        while True:
            curToken = self.next()
            self.TokenList.append(curToken)
            if isLog is True:
                print(curToken.getDescription())
            if curToken.Type == "eof":
                break
        return self.TokenList

    def getType(self, inputStr):  # return the Type of the input string
        if self.isKeyword(inputStr) is True:  # keyword
            Type = "keyword"

        elif self.isInteger(inputStr) is True:  # integer
            Type = "integer"

        elif self.isIdentifier(inputStr) is True:  # identifier
            Type = "identifier"

        else:
            Type = "bad input"  # bad input
        return Type

    def isKeyword(self, inputStr):  # input string is Keyword
        if inputStr in GlobalVal.KEYWORD or inputStr in GlobalVal.DELIMITER:
            return True
        return False

    def isInteger(self, inputStr):  # integer = digit {digit}.
        for i in range(len(inputStr)):
            if inputStr[i] not in GlobalVal.DIGIT:
                return False
        return True

    def isIdentifier(self, inputStr):  # identifier = letter {letter | digit}.
        if inputStr[0] not in GlobalVal.LETTER:
            return False
        for i in range(len(inputStr)):
            if inputStr[i] not in GlobalVal.DIGIT and inputStr[i] not in GlobalVal.LETTER:
                return False
        return True
