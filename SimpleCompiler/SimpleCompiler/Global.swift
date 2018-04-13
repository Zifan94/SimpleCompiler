//
//  Global.swift
//  SimpleCompiler
//
//  Created by Zifan  Yang on 4/12/18.
//  Copyright © 2018 Zifan  Yang. All rights reserved.
//

import Foundation

class Global{
    let KEYWORD : Set<String> = ["PROGRAM", "BEGIN", "END", "CONST", "TYPE", "VAR", "ARRAY", "OF", "RECORD", "IF","THEN", "ELSE", "REPEAT", "UNTIL", "WHILE", "DO", "WRITE", "READ", "DIV", "MOD"]
    let DIGIT : Set<String> = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    let LETTER : Set<String> = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y" ,"z", "A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
    let SKIP : Set<String> = [" ", "    ", "\n", "\r"]
    let DELIMITER : Set<String> = [";", ".", "=", ":", "+", "-", "*", "(", ")", ":=", "#", "<", ">", "<=", ">=", "[", "]", ","]
    let DOUBLE_DELIMITER : Set<String> = [":=", "<=", ">="]
    let COMMENT : Set<String> = ["(*", "*)"]
}
