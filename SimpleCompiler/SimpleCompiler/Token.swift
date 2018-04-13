//
//  Token.swift
//  SimpleCompiler
//
//  Created by Zifan  Yang on 4/12/18.
//  Copyright © 2018 Zifan  Yang. All rights reserved.
//

import Foundation

class Token {
    var type:String = ""             // "keyword", "identifier", "integer", "eof"
    var Value_Str:String = ""        // store the origin string
    var Value_Int:Int = 0            // only valid when Type = "integer"
    var startPos:Int = -1            // start position in source file
    var endPos:Int = -1              // end position in source file
    var lineNum:Int = -1             // line number
    var posNum:Int = -1             // Position number
    var myErrHandler:ErrorHandler
    
    init(inputStr:String, type:String, firstPos:Int, lastPos:Int, lineNum:Int, posNum:Int, myErrHandler:ErrorHandler){
        self.Value_Str = inputStr
        self.startPos = firstPos
        self.endPos = lastPos
        self.lineNum = lineNum
        self.posNum = posNum
        self.myErrHandler = myErrHandler
    
        if type == "keyword"
        {
            self.type = "keyword"
        }
        else if type == "identifier"
        {
            self.type = "identifier"
        }
        else if type == "integer"
        {
            self.type = "integer"
            self.Value_Int = Int(inputStr)!
        }
        else if type == "eof"
        {
            self.type = "eof"
        }
        else
        {
            let ErrMsg = "Error: <Sanner> @(line "+String(self.lineNum)+", pos "+String(self.posNum)+") cannot create a Token with unknown Type: "+self.type
            self.myErrHandler.RecordScannerError(errMsg: ErrMsg, lineNum: self.lineNum , posNum: self.posNum)
        }
    }
    
    
}
