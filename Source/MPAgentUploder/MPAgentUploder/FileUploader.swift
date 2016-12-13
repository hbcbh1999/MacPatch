//
//  FileUploader.swift
//  MPAgentUploder
//
//  Created by Charles Heizer on 12/11/16.
//  Copyright © 2016 Lawrence Livermore Nat'l Lab. All rights reserved.
//

import Foundation
import Alamofire

class AlamofireSynchronous
{
    class func uploadRequest(multipartFormData: @escaping (MultipartFormData) -> Void, to: URLConvertible, method: HTTPMethod, headers: HTTPHeaders? = nil) -> UploadRequest? {
        
        let semaphore = DispatchSemaphore(value: 0)
        var result: UploadRequest? = nil
        
        MPAlamofire.upload(multipartFormData: multipartFormData, to: to, method: method, headers: headers) { (res: Alamofire.SessionManager.MultipartFormDataEncodingResult) in
            
            switch res {
                case .success(let upload, _, _):
                    result = upload
                case .failure( _):
                    break
            }
            semaphore.signal()
        }
        
        _ = semaphore.wait(timeout: DispatchTime.distantFuture)
        return result
    }
}
