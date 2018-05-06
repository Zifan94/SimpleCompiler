//
//  Parser.swift
//  SimpleCompiler
//
//  Created by Zifan  Yang on 4/13/18.
//  Copyright © 2018 Zifan  Yang. All rights reserved.
//

import Foundation
import UIKit

class Parser {
    var tokenList:[Token]  = []
    var curPos:Int = 1
    var current:Token
    var last:Token
    var myErrHandler:ErrorHandler
    var ob:Observer
    var hasBEGIN:Bool
    var myTextColor:textColor
    
    init(tokenList:[Token], myErrorHandler:ErrorHandler, ob:Observer) {
        for token in tokenList{
            self.tokenList.append(token)
        }
        self.myErrHandler = myErrorHandler
        self.curPos = 0
        self.current = self.tokenList[0]
        self.ob = ob
        self.hasBEGIN = false
        self.last = self.tokenList[0]
        self.myTextColor = textColor()
    }
    
    func parse() {
        self.Program_ST()
    }
    
    func next() {
        self.last = self.current
        self.curPos += 1
        self.current = self.tokenList[self.curPos]
    }
    
    func match(candidateList:[String], tmpColor:UIColor = UIColor.white) -> String{
        let curToken = self.current
        if curToken.type == "eof" && candidateList == ["eof"] {
            return "eof"
        }
        if curToken.type == "keyword" && candidateList.contains(curToken.Value_Str) {
            self.ob.match(curToken: curToken)
            self.current.setColor(color: tmpColor)
            self.next()
            return curToken.Value_Str
        }
        if curToken.type == "identifier" && candidateList == ["identifier"] {
            self.ob.match(curToken: curToken)
            self.current.setColor(color: tmpColor)
            self.next()
            return curToken.Value_Str
        }
        if curToken.type == "integer" && candidateList == ["integer"] {
            self.ob.match(curToken: curToken)
            self.current.setColor(color: self.myTextColor.PURPLE)
            self.next()
            return String(curToken.Value_Int)
        }
        var ErrMsg = "Error: <Parser> @(line "+String(curToken.lineNum)+", pos "+String(curToken.posNum)+") cannot match current token "
        ErrMsg += curToken.getDescription()+" to "+String(describing: candidateList)
        self.myErrHandler.RecordParserError(errMsg: ErrMsg, lineNum: curToken.lineNum, posNum: curToken.posNum)
        return ""
    }
    
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // 1. Program = "PROGRAM" identifier ";" Declarations ["BEGIN" Instructions] "END" identifier "."
    func Program_ST() {
        self.ob.start(production: "Program")
        
        _ = self.match(candidateList: ["PROGRAM"], tmpColor:self.myTextColor.BLUE)
        let startIdToken = self.current
        let Program_Identifier_Start = match(candidateList: ["identifier"], tmpColor:self.myTextColor.GREEN)
        _ = self.match(candidateList:[";"])
        
        if ["BEGIN", "END"].contains(self.current.Value_Str) == false {
            self.Declarations_ST()
        }
        else {
            self.ob.start(production: "Declarations")
            self.ob.stop(production: "Declarations")
        }
        
        if self.current.type == "keyword" && self.current.Value_Str == "BEGIN" {
            self.hasBEGIN = true
            _ = self.match(candidateList: ["BEGIN"])
            self.Instructions_ST()
        }
        _ = match(candidateList: ["END"], tmpColor:self.myTextColor.BLUE)
        let endIdToken = self.current
        let Program_Identifier_End = match(candidateList: ["identifier"], tmpColor:self.myTextColor.GREEN)
        self.Check_Program_Identifier(startId: Program_Identifier_Start, endID: Program_Identifier_End, startIdToken: startIdToken, endIdToken: endIdToken)
        _ = match(candidateList: ["."])
        _ = match(candidateList: ["eof"])
        
        self.ob.stop(production: "Program")
    }
    
    // 2. Declarations = { ConstDecl | TypeDecl | VarDecl }
    func Declarations_ST() {
        self.ob.start(production: "Declarations")
        
        while self.current.type == "keyword" && ["CONST", "TYPE", "VAR"].contains(self.current.Value_Str) {
            if self.current.Value_Str == "CONST" {
                self.ConstDecl_ST()
            }
            else if self.current.Value_Str == "TYPE" {
                self.TypeDecl_ST()
            }
            else if self.current.Value_Str == "VAR" {
                self.VarDecl_ST()
            }
        }
        
        self.ob.stop(production: "Declarations")
    }
    
    // 3. ConstDecl = "CONST" { identifier "=" Expression ";" }
    func ConstDecl_ST() {
        self.ob.start(production: "ConstDecl")
        
        _ = match(candidateList: ["CONST"], tmpColor:self.myTextColor.RED)
        while self.current.type == "identifier" {
            _ = self.match(candidateList: ["identifier"])
            _ = self.match(candidateList: ["="])
            self.Expression_ST()
            _ = self.match(candidateList: [";"])
        }
        
        self.ob.stop(production: "ConstDecl")
    }
    
    // 4. TypeDecl = "TYPE" { identifier "=" Type ";" }
    func TypeDecl_ST() {
        self.ob.start(production: "TypeDecl")
        
        _ = self.match(candidateList: ["TYPE"], tmpColor:self.myTextColor.RED)
        while self.current.type == "identifier" {
            _ = self.match(candidateList: ["identifier"])
            _ = self.match(candidateList: ["="])
            self.Type_ST()
            _ = self.match(candidateList: [";"])
        }
        
        self.ob.stop(production: "TypeDecl")
    }
    
    // 5. VarDecl = "VAR" { IdentifierList ":" Type ";" }
    func VarDecl_ST() {
        self.ob.start(production: "VarDecl")
        
        _ = self.match(candidateList: ["VAR"], tmpColor:self.myTextColor.RED)
        while self.current.type == "identifier" {
            self.IdentifierList_ST()
            _ = self.match(candidateList: [":"])
            self.Type_ST()
            _ = self.match(candidateList: [";"])
        }
        
        self.ob.stop(production: "VarDecl")
    }
    
    // 6. Type = identifier | "ARRAY" Expression "OF" Type | "RECORD" { IdentifierList ":" Type ";" } "END"
    func Type_ST() {
        self.ob.start(production: "Type")
        
        if self.current.type == "identifier" {
            _ = self.match(candidateList: ["identifier"])
        }
        else if self.current.type == "keyword" && self.current.Value_Str == "ARRAY" {
            _ = self.match(candidateList: ["ARRAY"])
            self.Expression_ST()
            _ = self.match(candidateList: ["OF"])
            self.Type_ST()
        }
        else if self.current.type == "keyword" && self.current.Value_Str == "RECORD" {
            _ = self.match(candidateList: ["RECORD"])
            while self.current.type == "identifier" {
                self.IdentifierList_ST()
                _ = self.match(candidateList: [":"])
                self.Type_ST()
                _ = self.match(candidateList: [";"])
            }
            _ = self.match(candidateList: ["END"])
        }
        else {
            var errMsg = "Error: <Parser> @(line "+String(self.current.lineNum)+", pos "+String(self.current.posNum)+"), Cannot match current token "
            errMsg += self.current.getDescription()+" to an identifier, ARRAY or RECORD"
            self.myErrHandler.RecordParserError(errMsg: errMsg, lineNum: self.current.lineNum, posNum: self.current.posNum)
        }
        
        self.ob.stop(production: "Type")
    }
    
    // 7. Expression = ["+"|"-"] Term { ("+"|"-") Term }
    func Expression_ST() {
        self.ob.start(production: "Expression")
        
        if self.current.type == "keyword" && ["+", "-"].contains(self.current.Value_Str) {
            _ = self.match(candidateList: ["+", "-"])
        }
        self.Term_ST()
        
        while self.current.type == "keyword" && ["+", "-"].contains(self.current.Value_Str) {
            _ = self.match(candidateList: ["+", "-"])
            self.Term_ST()
        }
        
        self.ob.stop(production: "Expression")
    }
    
    // 8. Term = Factor { ("*"|"DIV"|"MOD") Factor }
    func Term_ST() {
        self.ob.start(production: "Term")
        
        self.Factor_ST()
        while self.current.type == "keyword" && ["*", "DIV", "MOD"].contains(self.current.Value_Str) {
            _ = self.match(candidateList: ["*", "DIV", "MOD"])
            self.Factor_ST()
        }
        
        self.ob.stop(production: "Term")
    }
    
    // 9. Factor = integer | Designator | "(" Expression ")"
    func Factor_ST() {
        self.ob.start(production: "Factor")
        
        if self.current.type == "integer" {
            _ = self.match(candidateList: ["integer"])
        }
        else if self.current.type == "identifier" {
            self.Designator_ST()
        }
        else if self.current.type == "keyword" && self.current.Value_Str == "(" {
            _ = self.match(candidateList: ["("])
            self.Expression_ST()
            _ = self.match(candidateList: [")"])
        }
        else {
            var errMsg = "Error: <Parser> @(line "+String(self.current.lineNum)+", pos "+String(self.current.posNum)+"), Cannot match current token "
            errMsg += self.current.getDescription()+" to integer, identifier or ("
            self.myErrHandler.RecordParserError(errMsg: errMsg, lineNum: self.current.lineNum, posNum: self.current.posNum)
        }
        
        self.ob.stop(production: "Factor")
    }
    
    // 10. Instructions = Instruction { ";" Instruciton }
    func Instructions_ST() {
        self.ob.start(production: "Instructions")
        
        self.Instruction_ST()
        while self.current.type == "keyword" && self.current.Value_Str == ";" {
            _ = self.match(candidateList: [";"])
            self.Instruction_ST()
        }
        
        self.ob.stop(production: "Instructions")
    }
    
    // 11. Instruction = Assign | If | Repeat | While | Read | Write
    func Instruction_ST() {
        self.ob.start(production: "Instruction")
        
        if self.current.type == "identifier" {
            self.Assign_ST()
        }
        else if self.current.type == "keyword" && self.current.Value_Str == "IF" {
            self.If_ST()
        }
        else if self.current.type == "keyword" && self.current.Value_Str == "REPEAT" {
            self.Repeat_ST()
        }
        else if self.current.type == "keyword" && self.current.Value_Str == "WHILE" {
            self.While_ST()
        }
        else if self.current.type == "keyword" && self.current.Value_Str == "READ" {
            self.Read_ST()
        }
        else if self.current.type == "keyword" && self.current.Value_Str == "WRITE" {
            self.Write_ST()
        }
        else {
            var errMsg = "Error: <Parser> @(line "+String(self.current.lineNum)+", pos "+String(self.current.posNum)+"), Cannot match current token "
            errMsg += self.current.getDescription()+" to identifier, IF, REPEAT, WHILE, READ or WRITE"
            self.myErrHandler.RecordParserError(errMsg: errMsg, lineNum: self.current.lineNum, posNum: self.current.posNum)
        }
        
        self.ob.stop(production: "Instruction")
    }
    
    // 12. Assign = Designator ":=" Expression
    func Assign_ST() {
        self.ob.start(production: "Assign")
        
        self.Designator_ST()
        _ = self.match(candidateList: [":="])
        self.Expression_ST()
        
        self.ob.stop(production: "Assign")
    }
    
    // 13. If = "IF" Condition "THEN" Instructions [ "ELSE" Instructions ] "END"
    func If_ST() {
        self.ob.start(production: "If")
        
        _ = self.match(candidateList: ["IF"])
        self.Condition_ST()
        _ = self.match(candidateList: ["THEN"])
        self.Instructions_ST()
        if self.current.type == "keyword" && self.current.Value_Str == "ELSE" {
            _ = self.match(candidateList: ["ELSE"])
            self.Instructions_ST()
        }
        _ = self.match(candidateList: ["END"])
        
        self.ob.stop(production: "If")
    }
    
    // 14. Repeat = "REPEAT" Instructions "UNTIL" Condition "END"
    func Repeat_ST() {
        self.ob.start(production: "Repeat")
        
        _ = self.match(candidateList: ["REPEAT"])
        self.Instructions_ST()
        _ = self.match(candidateList: ["UNTIL"])
        self.Condition_ST()
        _ = self.match(candidateList: ["END"])
        
        self.ob.stop(production: "Repeat")
    }
    
    // 15. While = "WHILE" Condition "DO" Instructions "END"
    func While_ST() {
        self.ob.start(production: "While")
        
        _ = self.match(candidateList: ["WHILE"])
        self.Condition_ST()
        _ = self.match(candidateList: ["DO"])
        self.Instructions_ST()
        _ = self.match(candidateList: ["END"])
        
        self.ob.stop(production: "While")
    }
    
    // 16. Condition = Expression ("="|"#"|"<"|">"|">="|"<=") Expression
    func Condition_ST() {
        self.ob.start(production: "Condition")
        
        self.Expression_ST()
        if self.current.type == "keyword" && ["=", "#", "<", ">", ">=", "<="].contains(self.current.Value_Str) {
            _ = self.match(candidateList: ["=", "#", "<", ">", ">=", "<="])
        }
        else {
            var errMsg = "Error: <Parser> @(line "+String(self.current.lineNum)+", pos "+String(self.current.posNum)+"), Cannot match current token "
            errMsg += self.current.getDescription()+" to =, #, <, >, <= or >="
            self.myErrHandler.RecordParserError(errMsg: errMsg, lineNum: self.current.lineNum, posNum: self.current.posNum)
        }
        self.Expression_ST()
        
        self.ob.stop(production: "Condition")
    }
    
    // 17. Write = "WRITE" Expression
    func Write_ST() {
        self.ob.start(production: "Write")
        
        _ = self.match(candidateList: ["WRITE"])
        self.Expression_ST()
        
        self.ob.stop(production: "Write")
    }
    
    // 18. Read = "READ" Designator
    func Read_ST() {
        self.ob.start(production: "Read")
        
        _ = self.match(candidateList: ["READ"])
        self.Declarations_ST()
        
        self.ob.stop(production: "Read")
    }
    
    // 19. Designator = identifier Selector
    func Designator_ST() {
        self.ob.start(production: "Designator")
        
        _ = self.match(candidateList: ["identifier"])
        self.Selector_ST()
        
        self.ob.stop(production: "Designator")
    }
    
    // 20. Selector = { "[" ExpressionList "]" | "." identifier }
    func Selector_ST() {
        self.ob.start(production: "Selector")
        
        while (self.current.type == "keyword" && self.current.Value_Str == "[") || (self.current.type == "keyword" && self.current.Value_Str == ".") {
            if self.current.type == "keyword" && self.current.Value_Str == "[" {
                _ = self.match(candidateList: ["["])
                self.ExpressionList_ST()
                _ = self.match(candidateList: ["]"])
            }
            else if self.current.type == "keyword" && self.current.Value_Str == "." {
                _ = self.match(candidateList: ["."])
                _ = self.match(candidateList: ["identifier"])
            }
        }
        
        self.ob.stop(production: "Selector")
    }
    
    // 21. IdentifierList = identifier { "," identifier }
    func IdentifierList_ST() {
        self.ob.start(production: "IdentifierList")
        
        _ = self.match(candidateList: ["identifier"])
        while self.current.type == "keyword" && self.current.Value_Str == "," {
            _ = self.match(candidateList: ["identifier"])
        }
        
        self.ob.stop(production: "IdentifierList")
    }
    
    // 22. ExpressionList = Expression { "," Expression }
    func ExpressionList_ST() {
        self.ob.start(production: "ExpressionList")
        
        self.Expression_ST()
        while self.current.type == "keyword" && self.current.Value_Str == "," {
            self.Expression_ST()
        }
        
        self.ob.stop(production: "ExpressionList")
    }
        
    
    
    
    /////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    func Check_Program_Identifier(startId:String, endID:String, startIdToken:Token, endIdToken:Token) {
        if startId != "" && endID != "" {
            if startId != endID {
                let errMsg = "Error: <Parser> @(line "+String(startIdToken.lineNum)+", pos "+String(startIdToken.posNum)+"), @(line "+String(endIdToken.lineNum)+", pos "+String(endIdToken.posNum)+"), Error: Cannot match Program Identifier "+startId+" to "+endID
                self.myErrHandler.RecordParserError(errMsg: errMsg, lineNum: 0, posNum: 0)
            }
        }
    }
}
