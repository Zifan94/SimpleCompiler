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
    
    func RecordScannerError(errMsg:String, lineNum:Int, posNum:Int){
        self.scannerErrList.append(errMsg)
        print("sadadsa")
    }
    
    func showScannerError() -> String{
        var retStr = ""
        for scannerErr in self.scannerErrList{
            retStr += scannerErr + "\n"
        }
        return retStr
    }
}
