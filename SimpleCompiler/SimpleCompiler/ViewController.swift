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
        
        NotificationCenter.default.addObserver(self, selector: #selector(ViewController.textChange(_:)), name: .UITextViewTextDidChange, object: nil)
    }

    
    @objc func textChange(_ notification: Notification)   {
        let myErrHandler = ErrorHandler()
        let myScanner = Scanner(sourceText: self.myTextView.text, myErrHandler: myErrHandler)
        let myTokenList = myScanner.all()
        let myErrMsg = myErrHandler.showScannerError()
        for item in myTokenList
        {
            print(item.type)
        }
        print(myErrMsg+"\n-----------------------\n")
    }
    @IBOutlet var TapBackground: UITapGestureRecognizer!
    
    override func didReceiveMemoryWarning() {
        super.didReceiveMemoryWarning()
        // Dispose of any resources that can be recreated.
    }
    
    

}


