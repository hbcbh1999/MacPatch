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
#import "MPCrypto.h"

#define AUTO_REG_KEY    @"999999999"
#define SRV_PUB_KEY     @"/Library/Application Support/MacPatch/.keys/ServerPub.pem";

#undef  ql_component
#define ql_component lcl_cMPAgentRegister

@interface MPAgentRegister ()
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
    NSError *err = nil;
    
    MPKeychain *mpk = [[MPKeychain alloc] init];
    mpk.overWriteKeyChainData = self.overWriteKeyChainData;
    
    NSString *keyHash = @"NA";
    NSDictionary *clientData = [mpk dictionaryFromKeychainWithKey:[mpk serviceLabelForClient] error:&err];
    if (err) {
        NSLog(@"Error: %@",err.localizedDescription);
        return FALSE;
    }
    
    err = nil;
    MPCrypto *mpc = [[MPCrypto alloc] init];
    keyHash = [mpc getHashFromStringForType:[clientData objectForKey:@"cKey"] type:@"SHA1"];
    if (err) {
        NSLog(@"Error: %@",err.localizedDescription);
        return FALSE;
    }
    
    result = [mpws getAgentRegStatus:nil error:&err];
    if (err) {
        NSLog(@"Error: %@",err.localizedDescription);
        return FALSE;
    }
    
    return result;
}

- (BOOL)clientIsRegisteredWithValidData
{
    BOOL result = FALSE;
    NSError *err = nil;
    
    MPKeychain *mpk = [[MPKeychain alloc] init];
    mpk.overWriteKeyChainData = self.overWriteKeyChainData;
    
    NSDictionary *serverData = [mpk dictionaryFromKeychainWithKey:[mpk serviceLabelForServer] error:&err];
    if (err) {
        NSLog(@"%@",err.localizedDescription);
        return FALSE;
    }
    NSLog(@"serverData: %@",serverData);
    
    NSData *pubKey;
    if ([serverData objectForKey:@"PubKey"]) {
        pubKey = [[serverData objectForKey:@"PubKey"] dataUsingEncoding:NSUTF8StringEncoding];
    } else {
        NSLog(@"Public key was not found using the PubKey attribute.");
        return FALSE;
    }
    
    
    NSDictionary *clientData = [mpk dictionaryFromKeychainWithKey:[mpk serviceLabelForClient] error:&err];
    if (err) {
        NSLog(@"%@",err.localizedDescription);
        return FALSE;
    }
    NSLog(@"clientData: %@",clientData);
    
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
    int res = 0;
    NSError *err = nil;
    
    if (![self addServerPublicKeyFileToKeychain:SRV_PUB_KEY error:&err]) {
        qlerror(@"Error adding server public key to keychain.");
        if (err) {
            qlerror(@"%@",err.localizedDescription);
        }
    }
    
    err = nil;
    NSDictionary *regDict = [self generateRegistrationPayload:&err];
    if (err) {
        qlerror(@"%@",err.localizedDescription);
        return 1;
    }
    
    err = nil;
    [self postRegistrationToServer:regDict regKey:aRegKey error:&err];
    if (err) {
        qlerror(@"%@",err.localizedDescription);
        return 1;
    }
    
    return res;
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

- (BOOL)addClientKeysToKeychain:(NSDictionary *)aClientKeys error:(NSError **)err
{
    MPKeychain *mpk = [[MPKeychain alloc] init];
    mpk.overWriteKeyChainData = self.overWriteKeyChainData;
    
    if (![aClientKeys objectForKey:@"priKeyPem"] || ![aClientKeys objectForKey:@"pubKeyPem"])
    {
        if (err != NULL) {
            *err = [mpk errorForOSStatus:errSecBadReq];
        } else {
            printf("%s\n",[[mpk errorForOSStatus:errSecBadReq].localizedDescription UTF8String]);
        }
        return NO;
    }
    
    NSDictionary *attributes = @{ @"PubKey" : [aClientKeys objectForKey:@"pubKeyPem"],
                                  @"PriKey" : [aClientKeys objectForKey:@"priKeyPem"],
                                  @"cKey"   : self.clientKey};
    
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

- (NSDictionary *)generateRegistrationPayload:(NSError **)err
{
    NSError *error = nil;
    // Create New Client Key and set class instance with the new key
    NSString *cKey = [[NSProcessInfo processInfo] globallyUniqueString];
    [self setClientKey:cKey];
    
    MPKeychain *mpk = [[MPKeychain alloc] init];
    mpk.overWriteKeyChainData = self.overWriteKeyChainData;
    
    // Get Server Data From the Keychain
    NSDictionary *serverData = [mpk dictionaryFromKeychainWithKey:[mpk serviceLabelForServer] error:&error];
    if (error) {
        if (err != NULL) {
            *err = error;
        } else {
            printf("%s\n",[error.localizedDescription UTF8String]);
        }
        return nil;
    }
    
    // Get the Server Public Key from the Server Data
    NSData *pubKey;
    if ([serverData objectForKey:@"PubKey"]) {
        pubKey = [[serverData objectForKey:@"PubKey"] dataUsingEncoding:NSUTF8StringEncoding];
    } else {
        NSDictionary *userInfo = @{NSLocalizedDescriptionKey: @"Public key was not found using the public key attribute."};
        NSError *_Err = [NSError errorWithDomain:@"MPAgentRegistrationDomain" code:99999 userInfo:userInfo];
        if (err != NULL) {
            *err = _Err;
        } else {
            printf("%s\n",[_Err.localizedDescription UTF8String]);
        }
        return nil;
    }
    
    // Encrypt the client key using the servers public key
    // also, SHA1 encode the client key. This will be used to
    // verify that we decoded the key properly and it matches.
    error = nil;
    MPCrypto *mpc = [[MPCrypto alloc] init];
    SecKeyRef srvPubKeyRef = [mpc getKeyRef:pubKey];
    NSString *encodedKey = [mpc encryptStringUsingKey:cKey key:srvPubKeyRef error:&error];
    NSString *hashOfKey =[mpc getHashFromStringForType:cKey type:@"SHA1"];
    if (error) {
        if (err != NULL) *err = error;
        return nil;
    }
    
    // Generate a RSA keypair for the Agent using 2048 bit key size
    error = nil;
    int keyRes = [mpc generateRSAKeyPairOfSize:2048 error:&error];
    if (error || keyRes != 0) {
        if (err != NULL) {
            *err = error;
            return nil;
        }
    }
    
    // Put both keys in to a dictionary that will be stored in the
    // keychain for the client.
    error = nil;
    NSDictionary *clientKeys = [mpc rsaKeysForRegistration:&error];
    if (error) {
        if (err != NULL) *err = error;
        return nil;
    }
    
    // Add the Client Keys to the Keychain, this will also add the
    // Agent Client Key to this entry as well
    error = nil;
    [self addClientKeysToKeychain:clientKeys error:&error];
    if (error) {
        if (err != NULL) *err = error;
        return nil;
    }
    
    // Create the Agent Registration Dictionary/Payload to send to the server
    @try
    {
        NSDictionary *regInfo;
        MPAgent *agent = [MPAgent  sharedInstance];
        regInfo = @{ @"cuuid": [agent g_cuuid],
                     @"cKey":encodedKey.copy,
                     @"CPubKeyPem":clientKeys[@"pubKeyPem"],
                     @"CPubKeyDer":clientKeys[@"pubKeyDer"],
                     @"ClientHash":hashOfKey,
                     @"HostName":[agent g_hostName],
                     @"SerialNo":[agent g_serialNo]};
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

- (BOOL)postRegistrationToServer:(NSDictionary *)aRegData regKey:(NSString *)regKey error:(NSError **)err
{
    NSError *error = nil;
    MPWebServices *xmpws = [[MPWebServices alloc] init];
    [xmpws postAgentReister:aRegData regKey:regKey error:&error];
    if (error) {
        if (err != NULL) *err = error;
        return NO;
    }
    return YES;
}

@end
