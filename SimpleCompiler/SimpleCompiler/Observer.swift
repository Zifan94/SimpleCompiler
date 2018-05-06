//
//  Observer.swift
//  SimpleCompiler
//
//  Created by Zifan  Yang on 4/13/18.
//  Copyright © 2018 Zifan  Yang. All rights reserved.
//

import Foundation

class Observer {
    var output:String = ""
    var spaceCnt:Int = 0
    
    init() {
        self.output = ""
        self.spaceCnt = 0
    }
    
    func start(production:String) {
        var spaceStr = ""
        for _ in 0...(self.spaceCnt) {
            spaceStr += " "
        }
        self.output += spaceStr + production + "\n"
        self.spaceCnt += 2
    }
    
    func stop(production:String) {
        self.spaceCnt -= 2
    }
    
    func match(curToken:Token) {
        var spaceStr = ""
        for _ in 0...self.spaceCnt-1 {
            spaceStr += " "
        }
        self.output += spaceStr + curToken.getDescription() + "\n"
    }
    
    func show() -> String {
        return self.output
    }
    
}
