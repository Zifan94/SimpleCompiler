//
//  Stack.swift
//  SimpleCompiler
//
//  Created by Zifan  Yang on 4/12/18.
//  Copyright © 2018 Zifan  Yang. All rights reserved.
//

import Foundation
class Stack {
    var stack: [AnyObject]
    init() {
        stack = [AnyObject]()
    }
    func push(object: AnyObject) {
        stack.append(object)
    }
    func pop() -> AnyObject? {
        if !isEmpty() {
            return stack.removeLast()
        } else {
            return nil
        }
    }
    func isEmpty() -> Bool {
        return stack.isEmpty
    }
    func peek() -> AnyObject? {
        return stack.last
    }
    func size() -> Int {
        return stack.count
    }
}
