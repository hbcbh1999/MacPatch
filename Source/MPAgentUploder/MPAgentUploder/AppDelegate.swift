//
//  AppDelegate.swift
//  MPAgentUploder
//
//  Created by Charles Heizer on 12/7/16.
//  Copyright © 2016 Lawrence Livermore Nat'l Lab. All rights reserved.
//

import Cocoa
import Alamofire
import LogKit
var log = LXLogger()
var MPAlamofire = Alamofire.SessionManager()

@NSApplicationMain
class AppDelegate: NSObject, NSApplicationDelegate {

    
    let defaults = UserDefaults.standard
    
    func applicationDidFinishLaunching(_ aNotification: Notification) {
        // Insert code here to initialize your application

        log = LXLogger(endpoints: [
            LXRotatingFileEndpoint(
                baseURL: URL(fileURLWithPath: logPath),
                numberOfFiles: 7,
                maxFileSizeKiB: (10 * 1024 * 1024),
                minimumPriorityLevel: .all,
                dateFormatter: LXDateFormatter(formatString: "yyyy-MM-dd HH:mm:ss",timeZone: NSTimeZone.local),
                entryFormatter: LXEntryFormatter({ entry in return
                    "\(entry.dateTime) [\(entry.level)] [\(entry.fileName)] \(entry.functionName):\(entry.lineNumber) --- \(entry.message)"
                })
            )
        ])

        NotificationCenter.default.post(name: Notification.Name("setLogLevel"), object: nil)
    }

    func applicationWillTerminate(_ aNotification: Notification) {
        // Insert code here to tear down your application
    }
    
    lazy var preferencesWindowController: PreferencesWindowController  = {
        let wcSB = NSStoryboard(name: "Preferences", bundle: Bundle.main)
        // or whichever bundle
        return wcSB.instantiateInitialController() as! PreferencesWindowController
    }()
    
    @IBAction func showPreferencesWindow(_ sender: NSObject?)
    {
        self.preferencesWindowController.showWindow(self)
    }
    
    @IBAction func showLogFileInConsole(_ sender: NSObject?)
    {
        let logFile = NSHomeDirectory().stringByAppendingPathComponent(path: "Library/Logs/1_AgentUploader.log")
        NSWorkspace.shared().openFile(logFile, withApplication: "Console")
        
    }
}

