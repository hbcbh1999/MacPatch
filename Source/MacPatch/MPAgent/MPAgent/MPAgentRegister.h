//
//  MPAgentRegister.h
//  MPAgent
//
//  Created by Heizer, Charles on 8/8/14.
//  Copyright (c) 2014 LLNL. All rights reserved.
//

#import <Foundation/Foundation.h>

@class MPWebServices;

@interface MPAgentRegister : NSObject
{
    MPWebServices *mpws;
}

@property (nonatomic, strong) NSString *clientKey;
@property (nonatomic, strong) NSString *registrationKey;
@property (nonatomic, strong) NSString *hostName;
@property (nonatomic, assign) BOOL overWriteKeyChainData;


- (BOOL)clientIsRegistered;

- (int)registerClient;
- (int)registerClient:(NSString *)aRegKey;
- (int)registerClient:(NSString *)aRegKey hostName:(NSString *)hostName;

// Server Pub Key

- (BOOL)addServerPublicKeyFileToKeychain:(NSString *)aFilePath error:(NSError **)err;
- (BOOL)addServerPublicKeyStringToKeychain:(NSString *)aPubKeyString error:(NSError **)err;

// Misc
- (NSDictionary *)generateRegistrationPayload:(NSError **)err;
- (BOOL)postRegistrationToServer:(NSDictionary *)aRegData regKey:(NSString *)regKey error:(NSError **)err;

@end
