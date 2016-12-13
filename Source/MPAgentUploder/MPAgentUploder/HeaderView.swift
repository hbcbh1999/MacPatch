//
//  HeaderView.swift
//  MPAgentUploder
//
//  Created by Charles Heizer on 12/12/16.
//  Copyright © 2016 Lawrence Livermore Nat'l Lab. All rights reserved.
//

import Foundation

class HeaderView : NSView {
    
    override func draw(_ dirtyRect: NSRect) {
        
        let gradient = NSGradient.init(starting: NSColor.darkGray, ending: NSColor.black)
        gradient?.draw(from: NSMakePoint(0,0), to: NSMakePoint(0,self.frame.size.height), options: .drawsAfterEndingLocation)
        /*
        let colorTop = NSColor(red: 48 / 255, green: 35 / 255, blue: 174 / 255, alpha: 1)
        let colorBottom = NSColor(red: 200 / 255, green: 109 / 255, blue: 215 / 255, alpha: 1)
        let gradient = NSGradient(colors: [colorTop, colorBottom])
        gradient?.draw(in: dirtyRect, angle: 45)
        */
    }
}
