//
//  AuthViewController.swift
//  MPAgentUploder
//
//  Created by Charles Heizer on 12/7/16.
//  Copyright © 2016 Lawrence Livermore Nat'l Lab. All rights reserved.
//

import Cocoa
import Alamofire

protocol AuthViewControllerDelegate: class {
    func didFinishAuthRequest(sender: AuthViewController, token:String)
}

class AuthViewController: NSViewController
{
    
    var delegate: AuthViewControllerDelegate?
    
    var x_mpServer: String?
    var x_mpPort: String?
    var x_useSSL: Int?
    
    @IBOutlet weak var authUserID: NSTextField!
    @IBOutlet weak var authUserPass: NSSecureTextField!
    @IBOutlet weak var authProgressWheel: NSProgressIndicator!
    @IBOutlet weak var authStatusField: NSTextField!
    @IBOutlet weak var authRequestButton: NSButton!
    
    let defaults = UserDefaults.standard
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        if defaults.bool(forKey: "selfSigned") {
            MPAlamofire={ ()->Alamofire.SessionManager in
                let policies:[String:ServerTrustPolicy]=[self.x_mpServer!: .disableEvaluation]
                let manager=Alamofire.SessionManager(serverTrustPolicyManager:ServerTrustPolicyManager(policies:policies))
                return manager
            }()
        }
    }
    
    override var representedObject: Any? {
        didSet {
            // Update the view, if already loaded.
        }
    }

    @IBAction func makeAuthRequest(_ sender: Any)
    {
        self.authStatusField.stringValue = ""
        self.authProgressWheel.startAnimation(nil)
        
        let _ssl = (x_useSSL == NSOnState) ? "https" : "http"
        let _url: String = "\(_ssl)://\(x_mpServer!):\(x_mpPort!)\(URI_PREFIX)/auth/token"
        
        let _params: Parameters = ["authUser":authUserID.stringValue, "authPass":authUserPass.stringValue]
        
        MPAlamofire.request(_url, method: .post, parameters: _params, encoding: JSONEncoding.default).validate().responseJSON
        { response in

            switch response.result
            {
            case .failure(let error):
                self.authStatusField.stringValue = error.localizedDescription
            
            case .success(let resultData):
                
                var api_token = "NA"
                
                if let resultDict = resultData as? [String: Any] {
                    if let res = resultDict["result"] as? [String: Any] {
                        api_token = res["token"] as! String? ?? "NA"
                        
                        if let delegate = self.delegate {
                            delegate.didFinishAuthRequest(sender: self, token:api_token)
                        }
                        
                        self.dismiss(self)
                    }
                }
            }
 
            self.authProgressWheel.stopAnimation(nil)
        }
    }
}
