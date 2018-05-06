//
//  ViewController.swift
//  SimpleCompiler
//
//  Created by Zifan  Yang on 4/12/18.
//  Copyright © 2018 Zifan  Yang. All rights reserved.
//

import UIKit

class ViewController: UIViewController {

    @IBOutlet weak var myTextView: UITextView!
    @IBOutlet weak var errorTextView: UITextView!
    
    
    var cnt:Int = 0
    override func viewDidLoad() {
        super.viewDidLoad()
        
        self.myTextView.backgroundColor = UIColor(red: 0.25, green: 0.25, blue: 0.25, alpha: 1.0)
        self.myTextView.tintColor = UIColor.white
        
        NotificationCenter.default.addObserver(self, selector: #selector(ViewController.textChange(_:)), name: .UITextViewTextDidChange, object: nil)
    }

    
//    @objc func textChange(_ notification: Notification)   {  scanner tester
//        let myErrHandler = ErrorHandler()
//        let myScanner = Scanner(sourceText: self.myTextView.text, myErrHandler: myErrHandler)
//        let myTokenList = myScanner.all()
//        let myErrMsg = myErrHandler.showScannerError()
//        for item in myTokenList
//        {
//            print(item.type)
//        }
//        print(myErrMsg+"\n-----------------------\n")
//    }
    
    @objc func textChange(_ notification: Notification)   {
        let myErrHandler = ErrorHandler()
        let myScanner = Scanner(sourceText: self.myTextView.text, myErrHandler: myErrHandler)
        let myTokenList = myScanner.all()
        var myErrMsg = myErrHandler.showScannerError()
        
        let myObserver = Observer()
        let myParser = Parser(tokenList: myTokenList, myErrorHandler: myErrHandler, ob: myObserver)
        myParser.parse()
        myErrMsg += myErrHandler.showParserError()
        
        if myErrHandler.parserFlag == false && myErrHandler.scannerFlag == false {
            print("success!\n"+myObserver.show())
        }
        print(myErrMsg+"\n---------- "+String(self.cnt)+" -------------\n")

        self.cnt += 1
        
        self.myTextView.attributedText = self.addColor(orgStr: self.myTextView.text, tokenList: myTokenList)

    }
    
    func addColor(orgStr:String, tokenList:[Token]) -> NSMutableAttributedString {
        let attrStr = NSMutableAttributedString(string: orgStr)
        for i in 0...(tokenList.count-1) {
            if i == tokenList.count-1 {
                break
            }
            let curToken = tokenList[i]
            let nextToken = tokenList[i+1]
            let start = curToken.startPos
            let len = nextToken.startPos - curToken.startPos
//            let str = NSString(string: orgStr)
            let theRange = NSRange(location: start, length: len)
            
            attrStr.addAttribute(NSAttributedStringKey.foregroundColor, value:curToken.tokenColor, range: theRange)
            attrStr.addAttribute(NSAttributedStringKey.font, value: UIFont(name:"AppleSDGothicNeo-SemiBold", size: CGFloat(24.4))!, range: theRange)
        }
        return attrStr
    }
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    

}


