//
//  Scanner.swift
//  SimpleCompiler
//
//  Created by Zifan  Yang on 4/12/18.
//  Copyright © 2018 Zifan  Yang. All rights reserved.
//

import Foundation

class Scanner{
    var sourceText: String = ""
    var nextPos:Int = 0
    var curLine:Int = 1
    var curPos:Int = 1
    var totalLen:Int = -1
    var TokenList:[Token]  = []
    var isCommentStack:Stack
    var getUnaccepableStr:Int = -1
    var myErrHandler:ErrorHandler
    var GlobalVal:Global

    
    init(sourceText:String, myErrHandler:ErrorHandler) {
        self.sourceText += sourceText+" "
        self.nextPos = 0
        self.totalLen = self.sourceText.count-1
        self.TokenList = []
        self.isCommentStack = Stack()
        self.getUnaccepableStr = -1
        self.myErrHandler = myErrHandler
        self.GlobalVal = Global()
    }

    func next() -> Token
    {
        if self.getUnaccepableStr >= 0
        {
            let ErrMsg = "Error: <Sanner> @(line "+String(self.curLine)+", pos "+String(self.curPos)+") cannot accept "+(self.sourceText as NSString).substring(with: NSMakeRange(self.getUnaccepableStr, 1))
            self.myErrHandler.RecordScannerError(errMsg: ErrMsg, lineNum: self.curLine , posNum: self.curPos)
        }
        // reaching the end of the source file which is the space we added manually
        if self.nextPos == self.totalLen
        {
            let newToken = Token(inputStr: "eof", type: "eof", firstPos: self.nextPos, lastPos: self.nextPos, lineNum: self.curLine, posNum: self.curPos, myErrHandler: self.myErrHandler)
            self.nextPos += 1
//            self.curPos += 1
            return newToken
        }
        if self.nextPos > self.totalLen { // next() is called after eof returned
            let ErrMsg = "Error: <Scanner> Cannot call next() after eof returned"
            self.myErrHandler.RecordScannerError(errMsg: ErrMsg, lineNum: 0 , posNum: 0)
        }
        
        var startPos = self.nextPos
        var nextPos = self.nextPos
        var endPos = self.nextPos
        var reachFirstChar = false
        
        var resultStr = ""
        while nextPos < self.totalLen
        {
            let curChar = String(self.sourceText[self.sourceText.index(self.sourceText.startIndex, offsetBy: nextPos)])
            if (reachFirstChar == false && GlobalVal.SKIP.contains(curChar))
            {
                if curChar == "\n"
                {
                    self.curLine += 1
                    self.curPos = 0
                }
                startPos += 1
                nextPos += 1
                endPos += 1
                continue
            }
            // now curChar is the first char that make sense
            if reachFirstChar == false
            {
                reachFirstChar = true
                if GlobalVal.DELIMITER.contains(curChar) // DELIMITER
                {
                    let nextChar = String(self.sourceText[self.sourceText.index(self.sourceText.startIndex, offsetBy: nextPos+1)])
                    let curChar_nextChar = curChar + nextChar
                    if GlobalVal.DOUBLE_DELIMITER.contains(curChar_nextChar)  // Double DELIMITER: :=, <=, >=
                    {
                        resultStr += curChar_nextChar
                        endPos = nextPos + 1
                        nextPos += 2
                        break
                    }
                    else if GlobalVal.COMMENT.contains(curChar_nextChar)  // (*, *)
                    {
                        if curChar_nextChar == "(*"
                        {
                            self.isCommentStack.push(object: nextPos as AnyObject)
                            resultStr += curChar_nextChar
                            endPos = nextPos + 1
                            nextPos += 2
                            break
                        }
                        else if curChar_nextChar == "*)"
                        {
                            if self.isCommentStack.isEmpty() == false
                            {
                                self.isCommentStack.pop()
                                resultStr += curChar_nextChar
                                endPos = nextPos + 1
                                nextPos += 2
                                break
                            }
                            else  // found a *) but no (* before, just read in * and ) normally
                            {
                                resultStr += curChar
                                endPos = nextPos
                                nextPos += 1
                                break
                            }
                        }
                    }
                    else // Normal Delimiter
                    {
                        resultStr += curChar
                        endPos = nextPos
                        nextPos += 1
                        break
                    }
                }
                else  // normal LETTER or DIGIT
                {
                    resultStr += curChar
                    endPos = nextPos
                    nextPos += 1
                    continue
                }
            }
            if reachFirstChar == true
            {
                if GlobalVal.SKIP.contains(curChar) // SKIP at end, end scan
                {
                    break
                }
                else if GlobalVal.DELIMITER.contains(curChar)  // DELIMITER at end, end scan
                {
                    break
                }
                else  // normal LETTER or DIGIT, processing
                {
                    resultStr += curChar
                    endPos = nextPos
                    nextPos += 1
                    continue
                }
            }
        } // While end here
        
        
        if ((GlobalVal.COMMENT.contains(resultStr)) || (self.isCommentStack.isEmpty() == false))
        {
            self.nextPos = nextPos
            return next()
        }
        if resultStr == "" && nextPos >= self.totalLen // reach the end of source file
        {
            self.nextPos = nextPos
            return next()
        }
        else
        {
            self.nextPos = nextPos
            let curType = getType(resultStr: resultStr)
        
            if curType == "bad input"
            {
                var lastPos = resultStr.count
                while lastPos > 0
                {
                    let tmpStr = (resultStr as NSString).substring(to: lastPos)
                    let tmpType = getType(resultStr: tmpStr)
                    if tmpType == "bad input"
                    {
                        lastPos = lastPos - 1
                        continue
                    }
                    else
                    {
                        self.nextPos = nextPos - (resultStr.count - lastPos)
                        let newToken = Token(inputStr: tmpStr, type: tmpType, firstPos: startPos, lastPos: startPos+lastPos-1, lineNum: self.curLine, posNum: self.curPos, myErrHandler: self.myErrHandler)
                        self.getUnaccepableStr = self.nextPos
//                        self.curPos += 1
                        return newToken
                    }
                }
                let ErrMsg = "Error: <Sanner> @(line "+String(self.curLine)+", pos "+String(self.curPos)+") cannot accept "+resultStr
                self.myErrHandler.RecordScannerError(errMsg: ErrMsg, lineNum: self.curLine , posNum: self.curPos)
            }
            let newToken = Token(inputStr: resultStr, type: curType, firstPos: startPos, lastPos: endPos, lineNum: self.curLine, posNum: self.curPos, myErrHandler: self.myErrHandler)
//            self.curPos += 1
            return newToken
        }
    }
    
    func all() ->[Token]
    {
        if self.nextPos != 0
        {
            let ErrMsg = "Error: <Scanner> Scanner cannot call all() because next() is already called somewhere"
            self.myErrHandler.RecordScannerError(errMsg: ErrMsg, lineNum: self.curLine , posNum: self.curPos)
        }
        while true
        {
            let curToken = next()
            self.TokenList.append(curToken)
            if curToken.type == "eof"
            {
                break
            }
        }
        return self.TokenList
    }
    
    
    func getType(resultStr:String) -> String
    {
        if isKeyword(inputStr: resultStr) == true
        {
            return "keyword"
        }
        if isInteger(inputStr: resultStr) == true
        {
            return "integer"
        }
        if isIdentifier(inputStr: resultStr) == true
        {
            return "identifier"
        }
        return "bad input"
    }
    
    func isKeyword(inputStr:String) -> Bool
    {
        if GlobalVal.KEYWORD.contains(inputStr) || GlobalVal.DELIMITER.contains(inputStr)
        {
            return true
        }
        return false
    }
    
    func isInteger(inputStr:String) -> Bool
    {
        for i in 0...inputStr.count-1
        {
            if GlobalVal.DIGIT.contains((inputStr as NSString).substring(with: NSMakeRange(i, 1))) == false
            {
                return false
            }
        }
        return true
    }
    
    func isIdentifier(inputStr:String) -> Bool
    {
        if GlobalVal.LETTER.contains((inputStr as NSString).substring(with: NSMakeRange(0, 1))) == false
        {
            return false
        }
        for i in 0...inputStr.count-1
        {
            if GlobalVal.LETTER.contains((inputStr as NSString).substring(with: NSMakeRange(i, 1))) == false && GlobalVal.DIGIT.contains((inputStr as NSString).substring(with: NSMakeRange(i, 1))) == false
            {
                return false
            }
        }
        return true
    }
    
}
