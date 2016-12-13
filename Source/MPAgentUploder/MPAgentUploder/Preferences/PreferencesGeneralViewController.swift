//
//  PreferencesGeneralViewController.swift
//  MPAgentUploder
//
//  Created by Charles Heizer on 12/7/16.
//  Copyright © 2016 Lawrence Livermore Nat'l Lab. All rights reserved.
//

import Cocoa

class PreferencesGeneralViewController: NSViewController
{
    
    let defaults = UserDefaults.standard
    
    @IBOutlet weak var agentUploadButton: NSButton!
    @IBOutlet weak var loggingButton: NSButton!
    @IBOutlet weak var selfSignedButton: NSButton!
    
    // disable the layout constraint on the right side of the button, so the window doesn't briefly assume its final size before it's animated
    override func viewDidAppear() {
        let _agentUploadState = defaults.bool(forKey: "doNotUpload") ? NSOnState : NSOffState
        let _debugState = defaults.bool(forKey: "Debug")  ? NSOnState : NSOffState
        let _selfSignedState = defaults.bool(forKey: "selfSigned")  ? NSOnState : NSOffState
        
        self.agentUploadButton.state = _agentUploadState
        self.loggingButton.state = _debugState
        self.selfSignedButton.state = _selfSignedState
    }
    
    //@IBOutlet weak var constraint : NSLayoutConstraint!
    //var oldPriority : NSLayoutPriority!

    @IBAction func debugOption(_ sender: AnyObject) {
        NotificationCenter.default.post(name: Notification.Name("LogLevel"), object: nil)
    }
    
    @IBAction func uploadOption(_ sender: AnyObject) {
        NotificationCenter.default.post(name: Notification.Name("AgentUpload"), object: nil)
    }
    
    @IBAction func selfSignedOption(_ sender: AnyObject) {
        NotificationCenter.default.post(name: Notification.Name("SelfSigned"), object: nil)
    }

}
