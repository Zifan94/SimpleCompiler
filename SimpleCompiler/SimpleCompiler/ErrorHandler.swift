//
//  ErrorHandler.swift
//  SimpleCompiler
//
//  Created by Zifan  Yang on 4/12/18.
//  Copyright © 2018 Zifan  Yang. All rights reserved.
//

import Foundation

class ErrorHandler {
    var scannerErrList:[String] = []
    var scannerFlag:Bool = false
    var parserErrList:[String] = []
    var parserFlag:Bool = false
    
    func RecordScannerError(errMsg:String, lineNum:Int, posNum:Int){
        self.scannerErrList.append(errMsg)
        self.scannerFlag = true
    }
    
    func showScannerError() -> String{
        var retStr = ""
        for scannerErr in self.scannerErrList{
            retStr += scannerErr + "\n"
        }
        return retStr
    }
    
    
    
    
    func RecordParserError(errMsg:String, lineNum:Int, posNum:Int){
        self.parserErrList.append(errMsg)
        self.parserFlag = true
    }
    
    func showParserError() -> String{
        var retStr = ""
        for parserErr in self.parserErrList{
            retStr += parserErr + "\n"
        }
        return retStr
    }
}
