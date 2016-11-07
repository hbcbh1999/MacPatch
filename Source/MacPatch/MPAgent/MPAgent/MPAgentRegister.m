//
//  MPAgentRegister.m
//  MPAgent
//
//  Created by Heizer, Charles on 8/8/14.
//  Copyright (c) 2014 LLNL. All rights reserved.
//

#import "MPAgentRegister.h"

#import <SystemConfiguration/SystemConfiguration.h>

#import "MacPatch.h"
#import "MPAgent.h"

#define AUTO_REG_KEY @"999999999"

@interface MPAgentRegister ()

- (NSDictionary *)clientHashes;

@end

@implementation MPAgentRegister

@synthesize clientKey           = _clientKey;
@synthesize registrationKey     = _registrationKey;
@synthesize hostName            = _hostName;


- (id)init
{
    self = [super init];
    if (self)
    {
        self.hostName = (__bridge NSString *)SCDynamicStoreCopyLocalHostName(NULL);
        self.registrationKey = AUTO_REG_KEY;
        self.clientKey = [[NSProcessInfo processInfo] globallyUniqueString];
        self.overWriteKeyChainData = NO;
        mpws = [[MPWebServices alloc] init];
    }
    return self;
}

- (BOOL)clientIsRegistered
{
    BOOL result = FALSE;
    //NSError *err = nil;
    //NSString *res = [mpws getRegisterAgent:aRegKey hostName:hostName clientKey:clientKey error:&err];
    //NSLog(@"%@",res);
    return result;
}

- (int)registerClient
{
    return [self registerClient:nil hostName:nil];
}

- (int)registerClient:(NSString *)aRegKey
{
    return [self registerClient:aRegKey hostName:nil];
}

- (int)registerClient:(NSString *)aRegKey hostName:(NSString *)hostName
{
    //NSError *err = nil;
    //NSString *res = [mpws getRegisterAgent:aRegKey hostName:hostName clientKey:clientKey error:&err];
    //NSLog(@"%@",res);
    return 0;
}

- (int)registerClientToBeRemoved:(NSString *)aRegKey hostName:(NSString *)hostName
{
    //NSError *err = nil;
    //NSString *res = [mpws getRegisterAgent:aRegKey hostName:hostName clientKey:clientKey error:&err];
    //NSLog(@"%@",res);
    return 0;
}

- (BOOL)addServerPublicKeyFileToKeychain:(NSString *)aFilePath error:(NSError **)err
{
    NSFileManager *fm       = [NSFileManager defaultManager];
    MPKeychain    *mpk      = [[MPKeychain alloc] init];
    mpk.overWriteKeyChainData = self.overWriteKeyChainData;
    NSString      *pubKeyStr;
    NSError       *fmErr    = nil;
    
    
    if ([fm fileExistsAtPath:aFilePath]) {
        pubKeyStr = [NSString stringWithContentsOfFile:aFilePath encoding:NSUTF8StringEncoding error:&fmErr];
        if (fmErr) {
            if (err != NULL) {
                *err = fmErr;
            } else {
                printf("%s\n",[fmErr.localizedDescription UTF8String]);
            }
            return NO;
        }
    } else {
        if (err != NULL) {
            NSDictionary *userInfo = @{NSLocalizedDescriptionKey: @"Server Public key file was not found."};
            *err = [NSError errorWithDomain:@"MPAgentRegistrationDomain" code:99996 userInfo:userInfo];
        } else {
            printf("Error, file (%s) not found. \n",[aFilePath UTF8String]);
        }
        return NO;
    }

    NSDictionary *attributes = @{ @"PubKey" : pubKeyStr };
    NSError *error = nil;
    OSStatus *result = [mpk addDictionaryToKeychainWithKey:[mpk serviceLabelForServer] dictionary:attributes error:&error];
    if (error) {
        if (err != NULL) {
            *err = error;
        } else {
            printf("%s\n",[error.localizedDescription UTF8String]);
        }
        return NO;
    }
    if (result != noErr) {
        NSError *resErr = [mpk errorForOSStatus:result];
        if (err != NULL) {
            *err = resErr;
        } else {
            printf("%s\n",[resErr.localizedDescription UTF8String]);
        }
        return NO;
    }
    
    return YES;
}

- (BOOL)addServerPublicKeyStringToKeychain:(NSString *)aPubKeyString error:(NSError **)err
{
    MPKeychain *mpk = [[MPKeychain alloc] init];
    mpk.overWriteKeyChainData = self.overWriteKeyChainData;
    
    NSDictionary *attributes = @{ @"PubKey" : aPubKeyString };
    NSError *error = nil;
    OSStatus *result = [mpk addDictionaryToKeychainWithKey:[mpk serviceLabelForServer] dictionary:attributes error:&error];
    if (error) {
        printf("%s\n",[error.localizedDescription UTF8String]);
        return NO;
    }
    if (result != noErr) {
        NSError *resErr = [mpk errorForOSStatus:result];
        printf("%s\n",[resErr.localizedDescription UTF8String]);
        return NO;
    }
    
    return YES;
}

- (BOOL)addClientKeysToKeychain:(NSDictionary *)aClientKeys error:(NSError **)err
{
    MPKeychain *mpk = [[MPKeychain alloc] init];
    mpk.overWriteKeyChainData = self.overWriteKeyChainData;
    if (![aClientKeys objectForKey:@"priKeyPem"] || ![aClientKeys objectForKey:@"pubKeyPem"] || ![aClientKeys objectForKey:@"cKey"])
    {
        if (err != NULL) {
            *err = [mpk errorForOSStatus:errSecBadReq];
        }
        return NO;
    }

    NSDictionary *attributes = @{ @"PubKey" : [aClientKeys objectForKey:@"pubKeyPem"],
                                  @"PriKey" : [aClientKeys objectForKey:@"priKeyPem"],
                                  @"cKey"   : [aClientKeys objectForKey:@"cKey"]};
    NSError *error = nil;
    OSStatus *result = [mpk addDictionaryToKeychainWithKey:[mpk serviceLabelForClient] dictionary:attributes error:&error];
    if (error) {
        if (err != NULL) {
            *err = error;
        } else {
            printf("%s\n",[error.localizedDescription UTF8String]);
        }
        return NO;
    }
    
    if (result != noErr)
    {
        NSError *resErr = [mpk errorForOSStatus:result];
        if (err != NULL) {
            *err = resErr;
        } else {
            printf("%s\n",[resErr.localizedDescription UTF8String]);
        }
        return NO;
    }
    
    return YES;
}
/* OLD
- (NSDictionary *)generateRegistrationPayload:(NSError **)err
{
    NSError *error = nil;
    NSString *cKey = [[NSUUID UUID] UUIDString];
    MPKeychain *mpk = [[MPKeychain alloc] init];
    
    NSDictionary *serverData = [mpk dictionaryFromKeychainWithKey:[mpk serviceLabelForServer] error:&error];
    if (error) {
        if (err != NULL) {
            *err = error;
        }
        return nil;
    }
    
    NSData *pubKey;
    if ([serverData objectForKey:@"PubKey"]) {
        pubKey = [[serverData objectForKey:@"PubKey"] dataUsingEncoding:NSUTF8StringEncoding];
    } else {
        NSDictionary *userInfo = @{NSLocalizedDescriptionKey: @"Public key was not found using the PubKey attribute."};
        if (err != NULL) {
            *err = [NSError errorWithDomain:@"MPAgentRegistrationDomain" code:99999 userInfo:userInfo];
        }
        return nil;
    }
    
    RSACrypto *rsa = [[RSACrypto alloc] initWithPublicKey:pubKey];
    NSString *encodedKey = [rsa encryptAndReturnEncoded:cKey];
    
    error = nil;
    NSDictionary *clientKeys = [rsa genRSAKeysUsingSize:2048 error:&error];
    if (error) {
        if (err != NULL) {
            *err = error;
            return nil;
        }
    }
    error = nil;
    NSMutableDictionary *ckeysDict = [NSMutableDictionary dictionaryWithDictionary:clientKeys];
    [ckeysDict setObject:cKey forKey:@"cKey"];
    [self addClientKeysToKeychain:(NSDictionary *)ckeysDict error:&error];
    if (error) {
        if (err != NULL) {
            *err = error;
            return nil;
        }
    }
    @try
    {
        NSDictionary *regInfo;
        NSDictionary *cHash = [self clientHashes];
        MPAgent *agent = [MPAgent  sharedInstance];
        
        regInfo = @{ @"cuuid": [agent g_cuuid], @"cKey":encodedKey,
                     @"CPubKeyPem":clientKeys[@"pubKeyPem"],
                     @"CPubKeyDer":clientKeys[@"pubKeyDer"],
                     @"ClientHash":cHash[@"MPHash"]};
        
        return regInfo;
    }
    @catch (NSException *exception) {
        if (err != NULL) {
            *err = [NSError errorWithDomain:@"MPAgentRegistrationDomain" code:9998 userInfo:exception.userInfo];
        }
        
        return nil;
    }
    
    // Should not get here
    NSDictionary *userInfo = @{NSLocalizedDescriptionKey: @"Reached end of method registration payload."};
    if (err != NULL) {
        *err = [NSError errorWithDomain:@"MPAgentRegistrationDomain" code:99997 userInfo:userInfo];
    }
    return nil;
}
*/

- (NSDictionary *)generateRegistrationPayload:(NSError **)err
{
    NSError *error = nil;
    NSString *cKey = [[NSUUID UUID] UUIDString];
    MPKeychain *mpk = [[MPKeychain alloc] init];
    mpk.overWriteKeyChainData = self.overWriteKeyChainData;
    
    NSDictionary *serverData = [mpk dictionaryFromKeychainWithKey:[mpk serviceLabelForServer] error:&error];
    if (error) {
        if (err != NULL) {
            *err = error;
        }
        return nil;
    }
    
    NSData *pubKey;
    if ([serverData objectForKey:@"PubKey"]) {
        pubKey = [[serverData objectForKey:@"PubKey"] dataUsingEncoding:NSUTF8StringEncoding];
    } else {
        NSDictionary *userInfo = @{NSLocalizedDescriptionKey: @"Public key was not found using the PubKey attribute."};
        if (err != NULL) {
            *err = [NSError errorWithDomain:@"MPAgentRegistrationDomain" code:99999 userInfo:userInfo];
        }
        return nil;
    }
    
    error = nil;
    MPCrypto *mpc = [[MPCrypto alloc] init];
    SecKeyRef srvPubKeyRef = [mpc getKeyRef:pubKey];
    NSString *encodedKey = [mpc encryptStringUsingKey:cKey key:srvPubKeyRef error:&error];
    if (error) {
        if (err != NULL) *err = error;
        return nil;
    }
    /* Remove Before release
     
    NSLog(@"cKey: %@",cKey);
    NSLog(@"cKey Encoded: %@",encodedKey);
    
    error = nil;
    NSData *priKeyData = [NSData dataWithContentsOfFile:@"/tmp/server_pri.pem"];
    SecKeyRef srvPriKeyRef = [mpc getKeyRef:priKeyData];
    NSString *decodedKey = [mpc decryptStringUsingKey:encodedKey key:srvPriKeyRef error:&error];
    if (error) {
        if (err != NULL) *err = error;
        return nil;
    }
    NSLog(@"cKey Decoded: %@",decodedKey);
    */
    
    error = nil;
    int keyRes = [mpc generateRSAKeyPairOfSize:2048 error:&error];
    if (error || keyRes != 0) {
        if (err != NULL) {
            *err = error;
            return nil;
        }
    }
    
    error = nil;
    NSDictionary *clientKeys = [mpc rsaKeysForRegistration:&error];
    if (error) {
        if (err != NULL) *err = error;
        return nil;
    }
    
    error = nil;
    NSMutableDictionary *ckeysDict = [NSMutableDictionary dictionaryWithDictionary:clientKeys];
    [ckeysDict setObject:cKey forKey:@"cKey"];
    [self addClientKeysToKeychain:(NSDictionary *)ckeysDict error:&error];
    if (error) {
        if (err != NULL) *err = error;
        return nil;
    }
    @try
    {
        NSDictionary *regInfo;
        NSDictionary *cHash = [self clientHashes];
        MPAgent *agent = [MPAgent  sharedInstance];
        
        regInfo = @{ @"cuuid": [agent g_cuuid], @"cKey":encodedKey,
                     @"CPubKeyPem":clientKeys[@"pubKeyPem"],
                     @"CPubKeyDer":clientKeys[@"pubKeyDer"],
                     @"ClientHash":cHash[@"MPHash"]};
        
        return regInfo;
    }
    @catch (NSException *exception) {
        if (err != NULL) {
            *err = [NSError errorWithDomain:@"MPAgentRegistrationDomain" code:9998 userInfo:exception.userInfo];
        }
        
        return nil;
    }
    
    // Should not get here
    NSDictionary *userInfo = @{NSLocalizedDescriptionKey: @"Reached end of method registration payload."};
    if (err != NULL) {
        *err = [NSError errorWithDomain:@"MPAgentRegistrationDomain" code:99997 userInfo:userInfo];
    }
    return nil;
}

- (NSDictionary *)clientHashes
{
    MPCrypto *mpc = [[MPCrypto alloc] init];
    NSDictionary *result;
    NSString *mpAgentA = [mpc getHashForFileForType:AGENT type:@"SHA1"];
    NSString *mpAgentE = [mpc getHashForFileForType:AGENT_EXEC type:@"SHA1"];
    NSString *mpAgentW = [mpc getHashForFileForType:AGENT_WORKER type:@"SHA1"];
    NSString *mpTotal = [mpc getHashFromStringForType:[NSString stringWithFormat:@"%@%@%@",mpAgentA,mpAgentE,mpAgentW] type:@"SHA1"];
    mpc = nil;
    
    result = @{@"MPAgent":mpAgentA, @"MPAgentExec":mpAgentE, @"MPWorker":mpAgentW, @"MPHash":mpTotal};
    return result;
}

- (void)postRegistrationToServer:(NSDictionary *)aRegData
{
    NSError *err = nil;
    MPWebServices *xmpws = [[MPWebServices alloc] init];
    NSDictionary *res = [xmpws registerAgentUsingPayload:aRegData regKey:_registrationKey error:&err];
    if (err) {
        NSLog(@"Err: %@",err.localizedDescription);
    }
    
    NSLog(@"Res: %@",res);
}

@end
