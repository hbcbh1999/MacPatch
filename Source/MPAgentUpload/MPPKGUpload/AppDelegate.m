//
//  AppDelegate.m
/*
 Copyright (c) 2013, Lawrence Livermore National Security, LLC.
 Produced at the Lawrence Livermore National Laboratory (cf, DISCLAIMER).
 Written by Charles Heizer <heizer1 at llnl.gov>.
 LLNL-CODE-636469 All rights reserved.
 
 This file is part of MacPatch, a program for installing and patching
 software.
 
 MacPatch is free software; you can redistribute it and/or modify it under
 the terms of the GNU General Public License (as published by the Free
 Software Foundation) version 2, dated June 1991.
 
 MacPatch is distributed in the hope that it will be useful, but WITHOUT ANY
 WARRANTY; without even the IMPLIED WARRANTY OF MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE. See the terms and conditions of the GNU General Public
 License for more details.
 
 You should have received a copy of the GNU General Public License along
 with MacPatch; if not, write to the Free Software Foundation, Inc.,
 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 */
#import "AppDelegate.h"
#import "PreferenceController.h"
#import "MPCrypto.h"
#import "NSString+Helper.h"
#import "WebRequest.h"
#import <CommonCrypto/CommonDigest.h>
#include <stdlib.h>

#define MPADM_URI       @"Service/MPAdminService.cfc"
#define MP_BASE_URI     @"/api/v1"

#undef  ql_component
#define ql_component lcl_cMain

@interface AppDelegate (Private)

- (IBAction)showPreferencePanel:(id)sender;
- (void)populateFromDefaults;
- (void)populateDefaults;

- (void)extractPKG:(NSString *)aPath;
- (void)writePlistForPackage:(NSString *)aPlist;
- (void)showAlertForMissingIdentity;

- (NSString *)encodeURLString:(NSString *)aString;

@end

@implementation AppDelegate

@synthesize extractImage;
@synthesize agentConfigImage;
@synthesize writeConfigImage;
@synthesize flattenPackagesImage;
@synthesize compressPackgesImage;
@synthesize postPackagesImage;
@synthesize progressBar;
@synthesize serverAddress;
@synthesize serverPort;
@synthesize useSSL;
@synthesize extratContentsStatus;
@synthesize getAgentConfStatus;
@synthesize writeConfStatus;
@synthesize flattenPkgStatus;
@synthesize compressPkgStatus;
@synthesize postPkgStatus;
@synthesize uploadButton;
@synthesize identityName;
@synthesize signPKG;
@synthesize tmpDir = _tmpDir;
@synthesize agentID = _agentID;
@synthesize agentDict = _agentDict;
@synthesize updaterDict = _updaterDict;
@synthesize authToken = _authToken;
@synthesize authUserName;
@synthesize authUserPass;
@synthesize authStatus;
@synthesize authProgressWheel;
@synthesize authRequestButton;

- (void)awakeFromNib
{
    NSString *_logFile = [NSHomeDirectory() stringByAppendingPathComponent:@"Library/Logs/MPAgentUploader.log"];
    [LCLLogFile setPath:_logFile];
    
    NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
    if ([d objectForKey:@"Debug"]) {
        if ([[d objectForKey:@"Debug"] integerValue] == 1)
        {
            lcl_configure_by_name("*", lcl_vDebug);
            if ([d objectForKey:@"Echo"]) {
                if ([[d objectForKey:@"Echo"] integerValue] == 1) {
                    [LCLLogFile setMirrorsToStdErr:YES];
                }
            }
            logit(lcl_vInfo,@"***** %@ v.%@ started -- Debug Enabled *****", [[[NSBundle mainBundle] infoDictionary] objectForKey:@"CFBundleName"],
                  [[[NSBundle mainBundle] infoDictionary] objectForKey:@"CFBundleShortVersionString"]);
        } else {
            lcl_configure_by_name("*", lcl_vInfo);
            logit(lcl_vInfo,@"***** %@ v.%@ started *****", [[[NSBundle mainBundle] infoDictionary] objectForKey:@"CFBundleName"],
                  [[[NSBundle mainBundle] infoDictionary] objectForKey:@"CFBundleShortVersionString"]);
        }
    } else {
        lcl_configure_by_name("*", lcl_vInfo);
        logit(lcl_vInfo,@"***** %@ v.%@ started *****", [[[NSBundle mainBundle] infoDictionary] objectForKey:@"CFBundleName"],
              [[[NSBundle mainBundle] infoDictionary] objectForKey:@"CFBundleShortVersionString"]);
    }

    fm = [NSFileManager defaultManager];
    [uploadButton setEnabled:NO];
    
    NSNotificationCenter *center = [NSNotificationCenter defaultCenter];
    [center addObserver:self selector:@selector(authTextDidChange:) name:NSControlTextDidChangeNotification object:authUserPass];
    [center addObserver:self selector:@selector(hostTextDidChange:) name:NSControlTextDidChangeNotification object:serverAddress];
    [center addObserver:self selector:@selector(uploadDisabledPref:) name:@"uploadPrefsStatus" object:nil];
    [center addObserver:self selector:@selector(loggingPref:) name:@"loggingPrefsStatus" object:nil];
    [center addObserver:self selector:@selector(webServicesType:) name:@"webServicesStatus" object:nil];
    [[NSNotificationCenter defaultCenter] postNotificationName:@"uploadPrefsStatus" object:self];
}

- (void)applicationDidFinishLaunching:(NSNotification *)aNotification
{
    // Insert code here to initialize your application
}

- (IBAction)showPreferencePanel:(id)sender
{
    // Is preferenceController nil?
    if (!preferenceController) {
        preferenceController = [[PreferenceController alloc] init];
    }
    [preferenceController showWindow:self];
}

- (void)populateFromDefaults
{
    // User Defaults
    NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
    if ([d objectForKey:@"dServerAddressState"]) {
        if ([d objectForKey:@"dServerAddress"]) {
            [serverAddress setStringValue:[d objectForKey:@"dServerAddress"]];
        }
    }
    if ([d objectForKey:@"dServerPortState"]) {
        if ([d objectForKey:@"dServerPort"]) {
            [serverPort setStringValue:[d objectForKey:@"dServerPort"]];
        }
    }
    if ([d objectForKey:@"dServerSSLState"]) {
        if ([d objectForKey:@"dServerSSL"]) {
            [useSSL setState:(NSInteger)[d objectForKey:@"dServerSSL"]];
        }
    }
    if ([d objectForKey:@"dIdentityState"]) {
        if ([d objectForKey:@"dIdentity"]) {
            [identityName setStringValue:[d objectForKey:@"dIdentity"]];
        }
    }
}

- (void)populateDefaults
{
    // User Defaults
    NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
    if ([d objectForKey:@"dServerAddressState"]) {
        if ((NSInteger)[d objectForKey:@"dServerAddressState"] == NSOnState) {
            [d setObject:serverAddress.stringValue forKey:@"dServerAddress"];
        } else {
            [d removeObjectForKey:@"dServerAddress"];
        }
    }
    if ([d objectForKey:@"dServerPort"]) {
        if ((NSInteger)[d objectForKey:@"dServerPortState"] == NSOnState) {
            [d setObject:serverPort.stringValue forKey:@"dServerPort"];
        } else {
            [d removeObjectForKey:@"dServerPort"];
        }
    }
    if ([d objectForKey:@"dServerPort"]) {
        if ((NSInteger)[d objectForKey:@"dServerSSLState"] == NSOnState) {
            [d setInteger:useSSL.state forKey:@"dServerSSL"];
        } else {
            [d removeObjectForKey:@"dServerSSL"];
        }
    }
    if ([d objectForKey:@"dServerPort"]) {
        if ((NSInteger)[d objectForKey:@"dIdentityState"] == NSOnState) {
            [d setObject:identityName.stringValue forKey:@"dIdentity"];
        } else {
            [d removeObjectForKey:@"dIdentity"];
        }
    }
    [d synchronize];
}

- (IBAction)showLogInConsole:(id)sender
{
    NSString *_logFile = [NSHomeDirectory() stringByAppendingPathComponent:@"Library/Logs/MPAgentUploader.log"];
    [[NSWorkspace sharedWorkspace] openFile:_logFile withApplication:@"Console"];
}

#pragma mark - sheet

-(IBAction)cancelAuthSheet:(id)sender
{
    [NSApp endSheet:authSheet];
    [authSheet orderOut:sender];
}

-(IBAction)makeAuthRequest:(id)sender
{
    NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
    if ([[d objectForKey:@"MP_REST_WS"] integerValue] == 1) {
        [self authRequestREST];
    } else {
        [self authRequest];
    }
}

-(void)authRequest
{
    [authProgressWheel setUsesThreadedAnimation:YES];
    [authProgressWheel startAnimation:authProgressWheel];
    [self.authStatus setStringValue:@"Authenticating..."];
    
    NSString *_host = serverAddress.stringValue;
    NSString *_port = serverPort.stringValue;
    NSString *_ssl = @"https";
    if (useSSL.state == NSOffState) {
        _ssl = @"http";
    } else {
        _ssl = @"https";
    }
    
    //-- Convert string into URL
    NSString *urlString = [NSString stringWithFormat:@"%@://%@:%@/%@?method=GetAuthToken&authUser=%@&authPass=%@",_ssl,_host,_port,MPADM_URI,[authUserName.stringValue urlEncode],[authUserPass.stringValue urlEncode]];
    NSMutableURLRequest *request =[[NSMutableURLRequest alloc] init];
    [request setURL:[NSURL URLWithString:urlString]];
    [request setHTTPMethod:@"GET"];
    
    NSError *error = nil;
    NSURLResponse *response;
    WebRequest *req = [[WebRequest alloc] init];
    NSData *responseData = [req sendSynchronousRequest:request returningResponse:&response error:&error];
    if (error)
    {
        qlerror(@"%@",error.localizedDescription);
        [self.authStatus setStringValue:error.localizedDescription];
        [self.authStatus setToolTip:error.localizedDescription];
        [self.authStatus performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        [authProgressWheel stopAnimation:authProgressWheel];
        return;
    }
    
    //-- JSON Parsing with response data
    error = nil;
    NSDictionary *result = [NSJSONSerialization JSONObjectWithData:responseData options:NSJSONReadingMutableContainers error:&error];
    qldebug(@"[makeAuthRequest]: %@",result);
    if ([result objectForKey:@"result"]) {
        if ([result objectForKey:@"errorno"]) {
            if ([[result objectForKey:@"errorno"] intValue] == 0)
            {
                [self setAuthToken:[result objectForKey:@"result"]];
            }
            else
            {
                [authStatus setStringValue:[result objectForKey:@"errormsg"]];
                [authStatus setToolTip:[result objectForKey:@"errormsg"]];
                [authStatus performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
                [authProgressWheel stopAnimation:authProgressWheel];
                return;
            }
        }
    }
    
    [NSApp endSheet:authSheet];
    [authSheet orderOut:self];
    [authProgressWheel stopAnimation:authProgressWheel];
    [self.authStatus setStringValue:@" "];
}

- (void)authTextDidChange:(NSNotification *)aNotification
{
    if ([[authUserName stringValue]length]>3 && [[authUserPass stringValue]length]>3) {
        [authRequestButton setEnabled:YES];
    } else {
        [authRequestButton setEnabled:NO];
    }
}

- (void)hostTextDidChange:(NSNotification *)aNotification
{
    /*
     if ([[serverAddress stringValue]length]>3) {
     [authRequestButton setEnabled:YES];
     } else {
     [authRequestButton setEnabled:NO];
     }
     */
}

- (void)uploadDisabledPref:(NSNotification *)aNotification
{
    NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
    if ([d objectForKey:@"dDoNotUpload"]) {
        if ([[d objectForKey:@"dDoNotUpload"] integerValue] == 1)
        {
            [postPkgStatus setStringValue:@"Upload is disabled for testing. Will open folder."];
            [postPkgStatus display];
        }
        else
        {
            [postPkgStatus setStringValue:@""];
            [postPkgStatus display];
        }
        [postPkgStatus performSelectorOnMainThread:@selector(display) withObject:nil waitUntilDone:YES];
    }
}

- (void)loggingPref:(NSNotification *)aNotification
{
    NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
    if ([d objectForKey:@"Debug"]) {
        if ([[d objectForKey:@"Debug"] integerValue] == 1)
        {
            lcl_configure_by_name("*", lcl_vDebug);
            qldebug(@"Debug logging is enabled.");
            if ([d objectForKey:@"Echo"]) {
                if ([[d objectForKey:@"Echo"] integerValue] == 1) {
                    [LCLLogFile setMirrorsToStdErr:YES];
                    qldebug(@"Echo STDERR to console is enabled.");
                }
            }
        } else {
            lcl_configure_by_name("*", lcl_vInfo);
        }
    } else {
        lcl_configure_by_name("*", lcl_vInfo);
    }
}

- (void)webServicesType:(NSNotification *)aNotification
{
    NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
    if ([d objectForKey:@"MP_REST_WS"]) {
        if ([[d objectForKey:@"MP_REST_WS"] integerValue] == 1)
        {
            qlinfo(@"Prefs changed, now using MacPatch 3.x REST web services.");
            
        } else {
            qlinfo(@"Prefs changed, now using MacPatch 2.x web services.");
        }
    }
}

#pragma mark - Main

- (void)resetInterface
{
    [uploadButton setEnabled:YES];
    [progressBar setIndeterminate:YES];
    [progressBar performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
    [extractImage setImage:[NSImage imageNamed:@"ClearDot"]];
    [extractImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
    [extratContentsStatus setStringValue:@""];
    [agentConfigImage setImage:[NSImage imageNamed:@"ClearDot"]];
    [agentConfigImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
    [getAgentConfStatus setStringValue:@""];
    [writeConfigImage setImage:[NSImage imageNamed:@"ClearDot"]];
    [writeConfigImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
    [writeConfStatus setStringValue:@""];
    [flattenPackagesImage setImage:[NSImage imageNamed:@"ClearDot"]];
    [flattenPackagesImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
    [flattenPkgStatus setStringValue:@""];
    [compressPackgesImage setImage:[NSImage imageNamed:@"ClearDot"]];
    [compressPackgesImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
    [compressPkgStatus setStringValue:@""];
    [postPackagesImage setImage:[NSImage imageNamed:@"ClearDot"]];
    [postPackagesImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
    [postPkgStatus setStringValue:@""];
}

- (IBAction)choosePackage:(id)sender
{
    NSOpenPanel *openDlg = [NSOpenPanel openPanel];
    [openDlg setMessage:@"Please select the MacPatch Client Installer zip file."];
    [openDlg setCanChooseFiles:YES];
    [openDlg setAllowedFileTypes:@[@"zip"]];
    [openDlg beginWithCompletionHandler:^(NSInteger result) {
        if(result==NSFileHandlingPanelOKButton) {
            for (NSURL *url in openDlg.URLs) {
                _packagePathField.stringValue = url.path;
                [uploadButton setEnabled:YES];
            }
        }
    }];
}

- (IBAction)choosePluginFolder:(id)sender
{
    NSOpenPanel *openDlg = [NSOpenPanel openPanel];
    [openDlg setMessage:@"Please select the MacPatch Client Installer zip file."];
    [openDlg setCanChooseDirectories:YES];
    [openDlg setCanChooseFiles:NO];
    [openDlg beginWithCompletionHandler:^(NSInteger result) {
        if(result==NSFileHandlingPanelOKButton) {
            for (NSURL *url in openDlg.URLs) {
                _pluginsPathField.stringValue = url.path;
            }
        }
    }];
}

- (IBAction)uploadPackage:(id)sender
{    
    if (!_authToken)
    {
        [NSApp beginSheet:authSheet modalForWindow:(NSWindow *)_window modalDelegate:self didEndSelector:@selector(beginUploadPackage) contextInfo:nil];
    } else {
        [NSThread detachNewThreadSelector:@selector(beginUploadPackage) toTarget:self withObject:nil];
    }
}

- (void)beginUploadPackage
{
    NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
    if (_authToken)
    {
        if ([[d objectForKey:@"MP_REST_WS"] integerValue] == 1) {
            [NSThread detachNewThreadSelector:@selector(uploadPackageRESTThread) toTarget:self withObject:nil];
        } else {
            [NSThread detachNewThreadSelector:@selector(uploadPackageThread) toTarget:self withObject:nil];
        }
    }
}

- (void)uploadPackageThread
{
    @autoreleasepool
    {
        NSUserDefaults *d = [NSUserDefaults standardUserDefaults];

        if (signPKG.state == NSOnState) {
            if ([identityName.stringValue length] <= 0) {
                NSAlert *alert = [[NSAlert alloc] init];
                [alert setAlertStyle:NSWarningAlertStyle];
                [alert setMessageText:@"Missing Identity"];
                [alert setInformativeText:@"You have choosen to sign the packages but did not enter an identity name. Please enter an identity name and try again."];
                [alert addButtonWithTitle:@"OK"];
                [alert performSelectorOnMainThread:@selector(runModal) withObject:nil waitUntilDone:NO];
                return;
            }
        }
        
        [self resetInterface];
        [[NSNotificationCenter defaultCenter] postNotificationName:@"uploadPrefsStatus" object:self];
        
        NSString *_host = serverAddress.stringValue;
        NSString *_port = serverPort.stringValue;
        NSString *_ssl = @"https";
        if (useSSL.state == NSOffState) {
            _ssl = @"http";
        } else {
            _ssl = @"https";
        }
        
        [uploadButton setEnabled:NO];
        [progressBar setUsesThreadedAnimation:YES];
        [progressBar setIndeterminate:YES];
        [progressBar startAnimation:progressBar];
        
        [extractImage setImage:[NSImage imageNamed:NSImageNameRemoveTemplate]];
        [extractImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        [self extractPKG:_packagePathField.stringValue];
        
        [agentConfigImage setImage:[NSImage imageNamed:NSImageNameRemoveTemplate]];
        [agentConfigImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        __block NSString *result = nil;
        // NSURLSession *session = [NSURLSession sharedSession];
        NSString *_url = [NSString stringWithFormat:@"%@://%@:%@/%@?method=AgentConfig&token=%@&user=%@",_ssl,_host,_port,MPADM_URI,[self encodeURLString:_authToken],authUserName.stringValue];
        
        NSMutableURLRequest *request =[[NSMutableURLRequest alloc] init];
        [request setURL:[NSURL URLWithString:_url]];
        [request setHTTPMethod:@"GET"];
        //-- Getting response form server
        NSError *error = nil;
        NSURLResponse *response;
        WebRequest *req = [[WebRequest alloc] init];
        NSData *responseData = [req sendSynchronousRequest:request returningResponse:&response error:&error];
        if (error)
        {
            qlerror(@"%@",error.localizedDescription);
            [progressBar stopAnimation:progressBar];
            [agentConfigImage setImage:[NSImage imageNamed:@"NoIcon"]];
            [uploadButton setEnabled:YES];
            [progressBar stopAnimation:progressBar];
            return;
        }
        
        NSError *bErr = nil;
        NSDictionary *json = [NSJSONSerialization JSONObjectWithData:responseData options:0 error:&bErr];
        if (bErr) {
            [agentConfigImage setImage:[NSImage imageNamed:@"NoIcon"]];
            [uploadButton setEnabled:YES];
            [progressBar stopAnimation:progressBar];
            return;
        }
        [agentConfigImage setImage:[NSImage imageNamed:@"YesIcon"]];
        result = [json objectForKey:@"result"];
        
        bErr = nil;
        NSString *_reqID = [self getRequestID:authUserName.stringValue error:&bErr];
        if (bErr) {
            [agentConfigImage setImage:[NSImage imageNamed:@"NoIcon"]];
            [uploadButton setEnabled:YES];
            [progressBar stopAnimation:progressBar];
            return;
        }
        
        [self setAgentID:_reqID];
        NSArray *pkgs1;
        
        bErr = nil;
        [writeConfigImage setImage:[NSImage imageNamed:NSImageNameRemoveTemplate]];
        [writeConfigImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        pkgs1 = [self writePlistForPackage:result error:&bErr];
        if (bErr) {
            [writeConfigImage setImage:[NSImage imageNamed:@"NoIcon"]];
            [uploadButton setEnabled:YES];
            [progressBar stopAnimation:progressBar];
            return;
        } else {
            [writeConfigImage setImage:[NSImage imageNamed:@"YesIcon"]];
        }
        [writeConfigImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        
        NSArray *pkgs2;
        bErr = nil;
        [flattenPackagesImage setImage:[NSImage imageNamed:NSImageNameRemoveTemplate]];
        [flattenPackagesImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        pkgs2 = [self flattenPackages:pkgs1 error:&bErr];
        if (bErr) {
            [flattenPackagesImage setImage:[NSImage imageNamed:@"NoIcon"]];
            [uploadButton setEnabled:YES];
            [progressBar stopAnimation:progressBar];
            return;
        } else {
            [flattenPackagesImage setImage:[NSImage imageNamed:@"YesIcon"]];
        }
        [flattenPackagesImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        
        NSArray *pkgs3;
        bErr = nil;
        [compressPackgesImage setImage:[NSImage imageNamed:NSImageNameRemoveTemplate]];
        [compressPackgesImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        pkgs3 = [self compressPackages:pkgs2 error:&bErr];
        if (bErr) {
            [compressPackgesImage setImage:[NSImage imageNamed:@"NoIcon"]];
            [uploadButton setEnabled:YES];
            [progressBar stopAnimation:progressBar];
            return;
        } else {
            [compressPackgesImage setImage:[NSImage imageNamed:@"YesIcon"]];
        }
        [compressPackgesImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        
        d = [NSUserDefaults standardUserDefaults];
        if ([d objectForKey:@"dDoNotUpload"]) {
            if ([[d objectForKey:@"dDoNotUpload"] integerValue] == 1)
            {
                NSString *p = [[pkgs3 objectAtIndex:0] stringByDeletingLastPathComponent];
                [[NSWorkspace sharedWorkspace] openFile:p];
                [progressBar stopAnimation:progressBar];
                [uploadButton setEnabled:YES];
                return;
            }
        }
        
        [postPackagesImage setImage:[NSImage imageNamed:NSImageNameRemoveTemplate]];
        [postPackagesImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        [self postFiles:(NSArray *)pkgs3 requestID:_reqID userID:authUserName.stringValue];
        [self postAgentPKGData:pkgs3];
        
        [progressBar stopAnimation:progressBar];
        [uploadButton setEnabled:YES];
    }
}

- (void)extractPKG:(NSString *)aPath
{
    _tmpDir = [NSTemporaryDirectory() stringByAppendingPathComponent:@"mpPkg"];
    if ([fm fileExistsAtPath:_tmpDir]) {
        [fm removeItemAtPath:_tmpDir error:NULL];
    }
    [fm createDirectoryAtPath:_tmpDir withIntermediateDirectories:YES attributes:nil error:nil];
    
    // Unzip it
    NSArray *tArgs = [NSArray arrayWithObjects:@"-x",@"-k",aPath,_tmpDir, nil];
    [NSTask launchedTaskWithLaunchPath:@"/usr/bin/ditto" arguments:tArgs];
    [NSThread sleepForTimeInterval:5.0];
    
    NSString *pkgName = [[_tmpDir stringByAppendingPathComponent:[aPath lastPathComponent]] stringByDeletingPathExtension];
    NSString *pkgExName = [_tmpDir stringByAppendingPathComponent:@"MPClientInstall"];
    NSArray *tArgs2 = [NSArray arrayWithObjects:@"--expand", pkgName, pkgExName, nil];
    [NSTask launchedTaskWithLaunchPath:@"/usr/sbin/pkgutil" arguments:tArgs2];
    [NSThread sleepForTimeInterval:5.0];
    
    [extractImage setImage:[NSImage imageNamed:@"YesIcon"]];
}

- (void)flattenPKG:(NSString *)aPKG
{
    BOOL signIt = NO;
    if (signPKG.state == NSOnState) {
        signIt = YES;
    }
    
    NSString *pkgName;
    if (signIt == YES) {
        pkgName = [NSString stringWithFormat:@"toSign_%@",[aPKG lastPathComponent]];
    } else {
        pkgName = [aPKG lastPathComponent];
    }
    
    NSString *pkgExName;
    if ([[pkgName pathExtension] isEqualToString:@"pkg"]) {
        pkgExName = [_tmpDir stringByAppendingPathComponent:pkgName];
    } else {
        pkgExName = [_tmpDir stringByAppendingPathComponent:[pkgName stringByAppendingPathExtension:@"pkg"]];
    }
    
    // Flatten the PKG
    NSArray *tArgs2 = [NSArray arrayWithObjects:@"/usr/sbin/pkgutil", @"--flatten", aPKG, pkgExName, nil];
    NSString *nscmd1 = [tArgs2 componentsJoinedByString:@" "];
    qldebug(@"%@",nscmd1);
    const char *cmd1 = [nscmd1 UTF8String];
    int res1 = system(cmd1);
    if (res1 != 0) {
        qlerror(@"Error trying to flatten %@",aPKG);
    } else {
        qlinfo(@"Flatten %@ succeeded.",aPKG);
    }
    [NSThread sleepForTimeInterval:1.0];

    
    // If Sign, then sign each pkg
    if (signIt == YES) {
        NSString *signedPkgName = [pkgExName stringByReplacingOccurrencesOfString:@"toSign_" withString:@""];
        NSString *_identity = [NSString stringWithFormat:@"\"%@\"",identityName.stringValue];
        NSArray *sArgs = [NSArray arrayWithObjects:@"/usr/bin/productsign", @"--sign", _identity, pkgExName, signedPkgName, nil];
        NSString *nscmd2 = [sArgs componentsJoinedByString:@" "];
        qldebug(@"%@",nscmd2);
        const char *cmd2 = [nscmd2 UTF8String];
        int res2 = system(cmd2);
        if (res2 != 0) {
            qlerror(@"Error trying to sign %@",aPKG);
        } else {
            qlinfo(@"Sign %@ succeeded",aPKG);
        }
        [NSThread sleepForTimeInterval:1.0];
    }
}

- (void)compressPKG:(NSString *)aPKG
{
    if (![fm fileExistsAtPath:aPKG]) {
        qlerror(@"No File Exists to compress %@",aPKG);
        qlerror(@"No File compress will occure.");
        return;
    }
    
    NSArray *tArgs = [NSArray arrayWithObjects:@"/usr/bin/ditto", @"-c",@"-k",aPKG,[aPKG stringByAppendingPathExtension:@"zip"], nil];
    NSString *nscmd = [tArgs componentsJoinedByString:@" "];
    qldebug(@"%@",nscmd);
    
    const char *cmd = [nscmd UTF8String];
    int res = system(cmd);
    if (res != 0) {
        qlerror(@"Error trying to compress %@",aPKG);
    } else {
        qlinfo(@"Compress %@ succeeded",aPKG);
    }

    [NSThread sleepForTimeInterval:1.0];
}

- (NSArray *)writePlistForPackage:(NSString *)aPlist error:(NSError **)err
{
    NSMutableArray *pkgs = [[NSMutableArray alloc] init];
    
    NSArray *dirFiles = [fm contentsOfDirectoryAtPath:[_tmpDir stringByAppendingPathComponent:@"MPClientInstall"] error:nil];
    NSArray *pkgFiles = [dirFiles filteredArrayUsingPredicate:[NSPredicate  predicateWithFormat:@"self ENDSWITH '.pkg'"]];
    NSString *fullPathScripts;
    NSString *fullPathPKG;
    NSString *expandedPKG = [_tmpDir stringByAppendingPathComponent:@"MPClientInstall"];
    for (NSString *pkg in pkgFiles)
    {
        
        
        fullPathPKG = [[_tmpDir stringByAppendingPathComponent:@"MPClientInstall"] stringByAppendingPathComponent:pkg];
        fullPathScripts = [fullPathPKG stringByAppendingPathComponent:@"Scripts/gov.llnl.mpagent.plist"];
        [aPlist writeToFile:fullPathScripts atomically:NO encoding:NSUTF8StringEncoding error:NULL];
        qlinfo(@"Write plist to %@",fullPathScripts);
        
        if ([fm fileExistsAtPath:[fullPathPKG stringByAppendingPathComponent:@"Scripts"]])
        {
            NSString *t;
            if ([[pkg lastPathComponent] isEqualToString:@"Base.pkg"]) {
                t = @"Agent";
                
                // Add Plugins
                NSString *pkgScriptPlugDir = [fullPathPKG stringByAppendingPathComponent:@"Scripts/Plugins"];
                [self addPluginsToBasePackage:pkgScriptPlugDir pluginsPath:_pluginsPathField.stringValue];
                if ([fm fileExistsAtPath:[expandedPKG stringByAppendingPathComponent:@"Resources/Background_done.png"]]) {
                    NSError *rmErr = nil;
                    [fm removeItemAtPath:[expandedPKG stringByAppendingPathComponent:@"Resources/Background.png"] error:&rmErr];
                    if (rmErr) {
                        qlerror(@"Error: %@",rmErr.localizedDescription);
                    }
                    [fm moveItemAtPath:[expandedPKG stringByAppendingPathComponent:@"Resources/Background_done.png"]
                                toPath:[expandedPKG stringByAppendingPathComponent:@"Resources/Background.png"]
                                 error:NULL];
                }
                
            } else {
                t = @"Updater";
            }
            [self readAndWriteVersionPlistToPath:[[_tmpDir stringByAppendingPathComponent:@"MPClientInstall"] stringByAppendingPathComponent:@"Resources/mpInfo.plist"] writeTo:[fullPathPKG stringByAppendingPathComponent:@"Scripts"] pkgType:t];
        }
        
        [pkgs addObject:fullPathPKG];
    }
    
    [pkgs addObject:[_tmpDir stringByAppendingPathComponent:@"MPClientInstall"]];
    
    return (NSArray *)pkgs;
}

- (void)addPluginsToBasePackage:(NSString *)pkgPath pluginsPath:(NSString *)aPluginsPath
{
    if (!aPluginsPath) return;
    if (![fm fileExistsAtPath:aPluginsPath]) return;
    
    NSError *pFileErr = nil;
    NSArray *pFiles = [fm contentsOfDirectoryAtPath:aPluginsPath error:&pFileErr];
    if (pFileErr) {
        qlerror(@"%@",pFileErr.localizedDescription);
        return;
    }
    
    if (!pFiles || ([pFiles count] <= 0) ) return;
    
    NSArray *pBundleFiles = [pFiles filteredArrayUsingPredicate:[NSPredicate  predicateWithFormat:@"self ENDSWITH '.bundle'"]];
    NSError *err = nil;
    
    if (![fm fileExistsAtPath:pkgPath]) {
        [fm createDirectoryAtPath:pkgPath withIntermediateDirectories:YES attributes:nil error:NULL];
    }
    
    for (NSString *plugin in pBundleFiles) {
        err = nil;
        qlinfo(@"Copy %@ to %@",[aPluginsPath stringByAppendingPathComponent:plugin],[pkgPath stringByAppendingPathComponent:plugin]);
        [fm copyItemAtPath:[aPluginsPath stringByAppendingPathComponent:plugin] toPath:[pkgPath stringByAppendingPathComponent:plugin] error:&err];
        if (err) {
            qlerror(@"%@",err.localizedDescription);
        }
    }
}

- (void)readAndWriteVersionPlistToPath:(NSString *)aInfoPath writeTo:(NSString *)aVerPath pkgType:(NSString *)aType
{
    NSDictionary *d = [NSDictionary dictionaryWithContentsOfFile:aInfoPath];
    NSDictionary *a = [NSDictionary dictionaryWithDictionary:[d objectForKey:aType]];
    NSMutableDictionary *da = [[NSMutableDictionary alloc] init];
    
    [da setObject:[a objectForKey:@"build"] forKey:@"build"];
    [da setObject:@"0" forKey:@"framework"];
    [da setObject:[[[a objectForKey:@"agent_version"] componentsSeparatedByString:@"."] objectAtIndex:0] forKey:@"major"];
    [da setObject:[[[a objectForKey:@"agent_version"] componentsSeparatedByString:@"."] objectAtIndex:1] forKey:@"minor"];
    [da setObject:[[[a objectForKey:@"agent_version"] componentsSeparatedByString:@"."] objectAtIndex:2] forKey:@"bug"];
    [da setObject:[a objectForKey:@"agent_version"] forKey:@"version"];
    
    [da writeToFile:[aVerPath stringByAppendingPathComponent:@".mpVersion.plist"] atomically:NO];
    
    if ([aType isEqualToString:@"Agent"]) {
        [da setObject:@"Base.pkg" forKey:@"pkg_name"];
        [da setObject:@"app" forKey:@"type"];
        [da setObject:[a objectForKey:@"osver"] forKey:@"osver"];
        [da setObject:[a objectForKey:@"agent_version"] forKey:@"agent_ver"];
        [da setObject:[a objectForKey:@"version"] forKey:@"ver"];
        [self setAgentDict:da];
    } else {
        [da setObject:@"Updater.pkg" forKey:@"pkg_name"];
        [da setObject:@"update" forKey:@"type"];
        [da setObject:[a objectForKey:@"osver"] forKey:@"osver"];
        [da setObject:[a objectForKey:@"agent_version"] forKey:@"agent_ver"];
        [da setObject:[a objectForKey:@"version"] forKey:@"ver"];
        [self setUpdaterDict:da];
    }
    
}

- (NSArray *)flattenPackages:(NSArray *)aPKGs error:(NSError **)err
{
    NSMutableArray *_pkgs = [[NSMutableArray alloc] init];
    
    for (NSString *pkg in aPKGs)
    {
        [self flattenPKG:pkg];
        if ([[[pkg lastPathComponent] pathExtension] isEqualToString:@"pkg"]) {
            [_pkgs addObject:[_tmpDir stringByAppendingPathComponent:[pkg lastPathComponent]]];
        } else {
            [_pkgs addObject:[_tmpDir stringByAppendingPathComponent:[[pkg lastPathComponent] stringByAppendingPathExtension:@"pkg"]]];
        }
    }
    
    return (NSArray *)_pkgs;
}

- (NSArray *)compressPackages:(NSArray *)aPKGs error:(NSError **)err
{
    NSMutableArray *_pkgs = [[NSMutableArray alloc] init];
    
    for (NSString *pkg in aPKGs)
    {
        [self compressPKG:pkg];
        [_pkgs addObject:[pkg stringByAppendingPathExtension:@"zip"]];
    }
    
    return (NSArray *)_pkgs;
}

- (void)postFiles:(NSArray *)aFiles requestID:(NSString *)aReqID userID:(NSString *)aUserID
{
    if (!aReqID) {
        qlerror(@"Error: request id was nil.");
        [postPackagesImage setImage:[NSImage imageNamed:@"NoIcon"]];
        return;
    }
    
    NSString *_host = serverAddress.stringValue;
    NSString *_port = serverPort.stringValue;
    NSString *_ssl = @"https";
    if (useSSL.state == NSOffState) {
        _ssl = @"http";
    } else {
        _ssl = @"https";
    }
    
    //-- Convert string into URL
    NSString *urlString = [NSString stringWithFormat:@"%@://%@:%@/Service/MPAgentFilePost.cfm",_ssl,_host,_port];
    //NSString *urlString = [NSString stringWithFormat:@"http://mplnx.llnl.gov:3601/Service/MPAgentFilePost.cfm"];
    NSMutableURLRequest *request =[[NSMutableURLRequest alloc] init];
    [request setURL:[NSURL URLWithString:urlString]];
    [request setHTTPMethod:@"POST"];
    
    NSString *boundary = @"14737809831466499882746641449";
    NSString *contentType = [NSString stringWithFormat:@"multipart/form-data; boundary=%@",boundary];
    [request addValue:contentType forHTTPHeaderField: @"Content-Type"];
    
    //-- Append data into posr url using following method
    NSMutableData *body = [NSMutableData data];
    
    //-- For Sending text
    
    [body appendData:[[NSString stringWithFormat:@"\r\n--%@\r\n",boundary] dataUsingEncoding:NSUTF8StringEncoding]];
    [body appendData:[[NSString stringWithFormat:@"Content-Disposition: form-data; name=\"%@\"\r\n\r\n",@"requestID"] dataUsingEncoding:NSUTF8StringEncoding]];
    [body appendData:[[NSString stringWithFormat:@"%@",aReqID] dataUsingEncoding:NSUTF8StringEncoding]];
    
    [body appendData:[[NSString stringWithFormat:@"\r\n--%@\r\n",boundary] dataUsingEncoding:NSUTF8StringEncoding]];
    [body appendData:[[NSString stringWithFormat:@"Content-Disposition: form-data; name=\"%@\"\r\n\r\n",@"userID"] dataUsingEncoding:NSUTF8StringEncoding]];
    [body appendData:[[NSString stringWithFormat:@"%@",aUserID] dataUsingEncoding:NSUTF8StringEncoding]];
    
    [body appendData:[[NSString stringWithFormat:@"\r\n--%@\r\n",boundary] dataUsingEncoding:NSUTF8StringEncoding]];
    [body appendData:[[NSString stringWithFormat:@"Content-Disposition: form-data; name=\"%@\"\r\n\r\n",@"token"] dataUsingEncoding:NSUTF8StringEncoding]];
    [body appendData:[[NSString stringWithFormat:@"%@",_authToken] dataUsingEncoding:NSUTF8StringEncoding]];
    
    for (NSString *_pkg in aFiles)
    {
        NSString *frmName;
        if ([[_pkg lastPathComponent] isEqualToString:@"Base.pkg.zip"]) {
            frmName = @"fBase";
        } else if ([[_pkg lastPathComponent] isEqualToString:@"Updater.pkg.zip"])
        {
            frmName = @"fUpdate";
        } else if ([[_pkg lastPathComponent] isEqualToString:@"MPClientInstall.pkg.zip"])
        {
            frmName = @"fComplete";
        }
        [body appendData:[[NSString stringWithFormat:@"\r\n--%@\r\n",boundary] dataUsingEncoding:NSUTF8StringEncoding]];
        [body appendData:[[NSString stringWithFormat:@"Content-Disposition:form-data; name=\"%@\"; filename=\"%@\"\r\n",frmName,[_pkg lastPathComponent]] dataUsingEncoding:NSUTF8StringEncoding]];
        [body appendData:[@"Content-Type: application/octet-stream\r\n\r\n" dataUsingEncoding:NSUTF8StringEncoding]];
        [body appendData:[NSData dataWithContentsOfFile:_pkg]];
    }
    
    //-- Sending data into server through URL
    [body appendData:[[NSString stringWithFormat:@"\r\n--%@--\r\n",boundary] dataUsingEncoding:NSUTF8StringEncoding]];
    [request setHTTPBody:body];
    
    //-- Getting response form server
    //NSData *responseData = [NSURLConnection sendSynchronousRequest:request returningResponse:nil error:nil];
    
    NSError *error = nil;
    NSURLResponse *response;
    WebRequest *req = [[WebRequest alloc] init];
    NSData *responseData = [req sendSynchronousRequest:request returningResponse:&response error:&error];
    if (error)
    {
        if (error) {
            qlerror(@"%@",error.localizedDescription);
        }
        
        [postPackagesImage setImage:[NSImage imageNamed:@"NoIcon"]];
        return;
    }
    
    //-- JSON Parsing with response data
    NSDictionary *result = [NSJSONSerialization JSONObjectWithData:responseData options:NSJSONReadingMutableContainers error:nil];
    qlinfo(@"[postFiles]: %@",result);
    if ([result objectForKey:@"errorno"]) {
        if ([[result objectForKey:@"errorno"] intValue] != 0) {
            [postPkgStatus setStringValue:[result objectForKey:@"errormsg"]];
            [postPackagesImage setImage:[NSImage imageNamed:@"NoIcon"]];
            return;
        } else {
            [postPackagesImage setImage:[NSImage imageNamed:@"YesIcon"]];
            return;
        }
    }
    
    [postPackagesImage setImage:[NSImage imageNamed:@"NoIcon"]];
}

- (void)postAgentPKGData:(NSArray *)aPKGs
{
    
    MPCrypto *mpc = [[MPCrypto alloc] init];
    NSMutableDictionary *d;
    NSString *pkgName;
    for (NSString *p in aPKGs)
    {
        pkgName = [[p lastPathComponent] stringByDeletingPathExtension];
        d = [[NSMutableDictionary alloc] init];
        [d setObject:self.agentID forKey:@"puuid"];
        [d setObject:pkgName forKey:@"pkg_name"];
        if ([pkgName isEqualToString:@"Base.pkg"]) {
            [d setObject:@"app" forKey:@"type"];
            [d setObject:[_agentDict objectForKey:@"agent_ver"] forKey:@"agent_ver"];
            [d setObject:[_agentDict objectForKey:@"ver"] forKey:@"version"];
            [d setObject:[_agentDict objectForKey:@"build"] forKey:@"build"];
            [d setObject:[mpc sha1HashForFile:p] forKey:@"pkg_hash"];
            [d setObject:[_agentDict objectForKey:@"osver"] forKey:@"osver"];
        } else if ([pkgName isEqualToString:@"Updater.pkg"]) {
            [d setObject:@"update" forKey:@"type"];
            [d setObject:[_updaterDict objectForKey:@"agent_ver"] forKey:@"agent_ver"];
            [d setObject:[_updaterDict objectForKey:@"ver"] forKey:@"version"];
            [d setObject:[_updaterDict objectForKey:@"build"] forKey:@"build"];
            [d setObject:[mpc sha1HashForFile:p] forKey:@"pkg_hash"];
            [d setObject:[_updaterDict objectForKey:@"osver"] forKey:@"osver"];
        } else {
            continue;
        }
        if (![self postAgentData:(NSDictionary *)d]) {
            break;
        }
    }
}

- (BOOL)postAgentData:(NSDictionary *)aConfig
{
    NSString *_host = serverAddress.stringValue;
    NSString *_port = serverPort.stringValue;
    NSString *_ssl = @"https";
    if (useSSL.state == NSOffState) {
        _ssl = @"http";
    } else {
        _ssl = @"https";
    }
    
    NSDictionary *d = [NSDictionary dictionaryWithDictionary:aConfig];
    
    //-- Convert string into URL
    NSString *dURL = [NSString stringWithFormat:@"&puuid=%@&type=%@&agent_ver=%@&version=%@&build=%@&pkg_name=%@&pkg_hash=%@&osver=%@",[d objectForKey:@"puuid"],[d objectForKey:@"type"],[d objectForKey:@"agent_ver"],[d objectForKey:@"version"],[d objectForKey:@"build"],[d objectForKey:@"pkg_name"],[d objectForKey:@"pkg_hash"],[d objectForKey:@"osver"]];
    NSString *urlString = [NSString stringWithFormat:@"%@://%@:%@/%@?method=postAgentData&%@&user=%@&token=%@",_ssl,_host,_port,MPADM_URI,dURL,authUserName.stringValue,[self encodeURLString:_authToken]];
    NSMutableURLRequest *request =[[NSMutableURLRequest alloc] init];
    [request setURL:[NSURL URLWithString:urlString]];
    [request setHTTPMethod:@"GET"];
    
    //-- Getting response form server
    NSError *error = nil;
    NSURLResponse *response;
    WebRequest *req = [[WebRequest alloc] init];
    NSData *responseData = [req sendSynchronousRequest:request returningResponse:&response error:&error];
    if (error)
    {
        if (error) {
            qlerror(@"%@",error.localizedDescription);
        }
        return NO;
    }
    
    //-- JSON Parsing with response data
    NSDictionary *result = [NSJSONSerialization JSONObjectWithData:responseData options:NSJSONReadingMutableContainers error:nil];
    qlinfo(@"[postAgentData]: %@",result);
    if ([result objectForKey:@"errorno"]) {
        if ([[result objectForKey:@"errorno"] intValue] != 0) {
            [postPkgStatus setStringValue:[result objectForKey:@"errormsg"]];
            [postPackagesImage setImage:[NSImage imageNamed:@"NoIcon"]];
            return NO;
        } else {
            [postPackagesImage setImage:[NSImage imageNamed:@"YesIcon"]];
            return YES;
        }
    }
    
    [postPackagesImage setImage:[NSImage imageNamed:@"NoIcon"]];
    return NO;
}

- (NSString *)getRequestID:(NSString *)aUserID error:(NSError **)err
{
    NSString *_host = serverAddress.stringValue;
    NSString *_port = serverPort.stringValue;
    NSString *_ssl = @"https";
    if (useSSL.state == NSOffState) {
        _ssl = @"http";
    } else {
        _ssl = @"https";
    }
    
    //-- Convert string into URL
    NSString *urlString = [NSString stringWithFormat:@"%@://%@:%@/%@?method=postAgentFiles&user=%@&token=%@",_ssl,_host,_port,MPADM_URI,authUserName.stringValue,[self encodeURLString:_authToken]];
    NSMutableURLRequest *request =[[NSMutableURLRequest alloc] init];
    [request setURL:[NSURL URLWithString:urlString]];
    [request setHTTPMethod:@"GET"];
    
    //-- Getting response form server
    NSError *error = nil;
    NSURLResponse *response;
    WebRequest *req = [[WebRequest alloc] init];
    NSData *responseData = [req sendSynchronousRequest:request returningResponse:&response error:&error];
    if (error)
    {
        if (error) {
            qlerror(@"%@",error.localizedDescription);
        }
        return nil;
    }
    
    //-- JSON Parsing with response data
    NSDictionary *result = [NSJSONSerialization JSONObjectWithData:responseData options:NSJSONReadingMutableContainers error:nil];
    qlinfo(@"[getRequestID]: %@",result);
    if ([result objectForKey:@"errorno"]) {
        if ([[result objectForKey:@"errorno"] intValue] != 0) {
            NSMutableDictionary *errDetails = [NSMutableDictionary dictionary];
            [errDetails setValue:[result objectForKey:@"errormsg"] forKey:NSLocalizedDescriptionKey];
            // populate the error object with the details
            *err = [NSError errorWithDomain:@"world" code:[[result objectForKey:@"errorno"] intValue] userInfo:errDetails];
            return nil;
        }
    }
    
    if ([result objectForKey:@"result"]) {
        return [result objectForKey:@"result"];
    } else {
        return nil;
    }
}

- (NSString *)encodeURLString:(NSString *)aString
{
    NSString *encodedString = (NSString *)CFBridgingRelease(CFURLCreateStringByAddingPercentEscapes(
                                                                                                    NULL,
                                                                                                    (CFStringRef)aString,
                                                                                                    NULL,
                                                                                                    (CFStringRef)@"!*'();:@&=+$,/?%#[]",
                                                                                                    kCFStringEncodingUTF8 ));
    return encodedString;
}

# pragma mark - REST Methods - MacPatch 3.x

-(void)authRequestREST
{
    [authProgressWheel setUsesThreadedAnimation:YES];
    [authProgressWheel startAnimation:authProgressWheel];
    [self.authStatus setStringValue:@"Authenticating..."];
    
    NSString *_host = serverAddress.stringValue;
    NSString *_port = serverPort.stringValue;
    NSString *_ssl = @"https";
    if (useSSL.state == NSOffState) {
        _ssl = @"http";
    } else {
        _ssl = @"https";
    }
    
    //-- Convert string into URL
    NSString *urlString = [NSString stringWithFormat:@"%@://%@:%@%@/auth/token",_ssl,_host,_port,MP_BASE_URI];
    NSDictionary *authDict = @{@"authUser":authUserName.stringValue,@"authPass":authUserPass.stringValue};
    
    NSMutableURLRequest *request =[[NSMutableURLRequest alloc] init];
    [request setURL:[NSURL URLWithString:urlString]];
    [request setHTTPMethod:@"POST"];
    
    NSData *requestData = [NSJSONSerialization dataWithJSONObject:authDict options:0 error:nil];
    [request setHTTPBody: requestData];
    [request setValue:[NSString stringWithFormat:@"%d", (int)[requestData length]] forHTTPHeaderField:@"Content-Length"];
    [request setValue:@"application/json; charset=utf-8" forHTTPHeaderField:@"Content-Type"];
    
    
    NSError *error = nil;
    NSURLResponse *response;
    WebRequest *req = [[WebRequest alloc] init];
    NSData *responseData = [req sendSynchronousRequest:request returningResponse:&response error:&error];
    if (error)
    {
        qlerror(@"%@",error.localizedDescription);
        [self.authStatus setStringValue:error.localizedDescription];
        [self.authStatus setToolTip:error.localizedDescription];
        [self.authStatus performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        [authProgressWheel stopAnimation:authProgressWheel];
        return;
    }
    
    //-- JSON Parsing with response data
    error = nil;
    NSDictionary *result = [NSJSONSerialization JSONObjectWithData:responseData options:NSJSONReadingMutableContainers error:&error];
    qldebug(@"[makeAuthRequest]: %@",result);
    if ([result objectForKey:@"result"]) {
        if ([result objectForKey:@"errorno"]) {
            if ([[result objectForKey:@"errorno"] intValue] == 0)
            {
                if ([[result objectForKey:@"result"] objectForKey:@"token"]) {
                    [self setAuthToken:[[result objectForKey:@"result"] objectForKey:@"token"]];
                } else {
                    [authStatus setStringValue:@"Error: token string not found."];
                    [authStatus setToolTip:@"Error: token string not found."];
                    [authStatus performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
                }
            }
            else
            {
                [authStatus setStringValue:[result objectForKey:@"errormsg"]];
                [authStatus setToolTip:[result objectForKey:@"errormsg"]];
                [authStatus performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
                [authProgressWheel stopAnimation:authProgressWheel];
                return;
            }
        }
    }
    
    [NSApp endSheet:authSheet];
    [authSheet orderOut:self];
    [authProgressWheel stopAnimation:authProgressWheel];
    [self.authStatus setStringValue:@" "];
}

- (void)postFilesREST:(NSArray *)aFiles
{
    NSString *aid = [[NSUUID UUID] UUIDString];
    
    NSString *_host = serverAddress.stringValue;
    NSString *_port = serverPort.stringValue;
    NSString *_ssl = @"https";
    if (useSSL.state == NSOffState) {
        _ssl = @"http";
    } else {
        _ssl = @"https";
    }
    
    NSDictionary *_basePKGData;
    NSDictionary *_updtPKGData;
    
    //-- Convert string into URL
    NSString *uri = @"api/v1/agent/upload";
    NSString *urlString = [NSString stringWithFormat:@"%@://%@:%@/%@/%@/%@",_ssl,_host,_port,uri,aid,_authToken];
    NSMutableURLRequest *request =[[NSMutableURLRequest alloc] init];
    [request setURL:[NSURL URLWithString:urlString]];
    [request setHTTPMethod:@"POST"];
    
    NSString *boundary = @"14737809831466499882746641449";
    NSString *contentType = [NSString stringWithFormat:@"multipart/form-data; boundary=%@",boundary];
    [request addValue:contentType forHTTPHeaderField: @"Content-Type"];
    
    //-- Append data into posr url using following method
    NSMutableData *body = [NSMutableData data];
    
    for (NSString *_pkg in aFiles)
    {
        NSString *frmName;
        NSString *_pkgFileName = [_pkg lastPathComponent];
        if ([_pkgFileName isEqualToString:@"Base.pkg.zip"]) {
            frmName = @"fBase";
            _basePKGData = [self agentPKGData:_pkg];
        } else if ([_pkgFileName isEqualToString:@"Updater.pkg.zip"])
        {
            frmName = @"fUpdate";
            _updtPKGData = [self agentPKGData:_pkg];
        } else if ([_pkgFileName isEqualToString:@"MPClientInstall.pkg.zip"])
        {
            frmName = @"fComplete";
        }
        [body appendData:[[NSString stringWithFormat:@"\r\n--%@\r\n",boundary] dataUsingEncoding:NSUTF8StringEncoding]];
        [body appendData:[[NSString stringWithFormat:@"Content-Disposition:form-data; name=\"%@\"; filename=\"%@\"\r\n",frmName,[_pkg lastPathComponent]] dataUsingEncoding:NSUTF8StringEncoding]];
        [body appendData:[@"Content-Type: application/octet-stream\r\n\r\n" dataUsingEncoding:NSUTF8StringEncoding]];
        [body appendData:[NSData dataWithContentsOfFile:_pkg]];
    }
    
    
    //-- Package(s) data
    NSDictionary *_pkgData = @{ @"app": _basePKGData, @"update": _updtPKGData};
    NSData *jsonData = [NSJSONSerialization dataWithJSONObject:_pkgData options:NSJSONWritingPrettyPrinted error:nil];
    
    [body appendData:[[NSString stringWithFormat:@"\r\n--%@\r\n",boundary] dataUsingEncoding:NSUTF8StringEncoding]];
    [body appendData:[@"Content-Disposition: form-data; name=\"data\"\r\n\r\n" dataUsingEncoding:NSUTF8StringEncoding]];
    [body appendData:jsonData];
    
    //-- Sending data into server through URL
    [body appendData:[[NSString stringWithFormat:@"\r\n--%@--\r\n",boundary] dataUsingEncoding:NSUTF8StringEncoding]];
    [request setHTTPBody:body];
    
    
    NSError *error = nil;
    NSURLResponse *response;
    WebRequest *req = [[WebRequest alloc] init];
    NSData *responseData = [req sendSynchronousRequest:request returningResponse:&response error:&error];
    if (error)
    {
        if (error) {
            qlerror(@"%@",error.localizedDescription);
        }
        
        [postPackagesImage setImage:[NSImage imageNamed:@"NoIcon"]];
        return;
    }
    
    //-- JSON Parsing with response data
    NSDictionary *result = [NSJSONSerialization JSONObjectWithData:responseData options:NSJSONReadingMutableContainers error:nil];
    qlinfo(@"[postFiles]: %@",result);
    if ([result objectForKey:@"errorno"]) {
        if ([[result objectForKey:@"errorno"] intValue] != 0) {
            [postPkgStatus setStringValue:[result objectForKey:@"errormsg"]];
            [postPackagesImage setImage:[NSImage imageNamed:@"NoIcon"]];
            return;
        } else {
            [postPackagesImage setImage:[NSImage imageNamed:@"YesIcon"]];
            return;
        }
    }
    
    [postPackagesImage setImage:[NSImage imageNamed:@"NoIcon"]];
}

- (void)uploadPackageRESTThread
{
    @autoreleasepool
    {
        NSUserDefaults *d = [NSUserDefaults standardUserDefaults];
        
        if (signPKG.state == NSOnState) {
            if ([identityName.stringValue length] <= 0) {
                NSAlert *alert = [[NSAlert alloc] init];
                [alert setAlertStyle:NSWarningAlertStyle];
                [alert setMessageText:@"Missing Identity"];
                [alert setInformativeText:@"You have choosen to sign the packages but did not enter an identity name. Please enter an identity name and try again."];
                [alert addButtonWithTitle:@"OK"];
                [alert performSelectorOnMainThread:@selector(runModal) withObject:nil waitUntilDone:NO];
                return;
            }
        }
        
        [self resetInterface];
        [[NSNotificationCenter defaultCenter] postNotificationName:@"uploadPrefsStatus" object:self];
        
        NSString *_host = serverAddress.stringValue;
        NSString *_port = serverPort.stringValue;
        NSString *_ssl = @"https";
        if (useSSL.state == NSOffState) {
            _ssl = @"http";
        } else {
            _ssl = @"https";
        }
        
        [uploadButton setEnabled:NO];
        [progressBar setUsesThreadedAnimation:YES];
        [progressBar setIndeterminate:YES];
        [progressBar startAnimation:progressBar];
        
        [extractImage setImage:[NSImage imageNamed:NSImageNameRemoveTemplate]];
        [extractImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        [self extractPKG:_packagePathField.stringValue];
        
        [agentConfigImage setImage:[NSImage imageNamed:NSImageNameRemoveTemplate]];
        [agentConfigImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        __block NSString *result = nil;
        
        NSString *_url = [NSString stringWithFormat:@"%@://%@:%@%@/agent/config/%@",_ssl,_host,_port,MP_BASE_URI, _authToken];
        //NSLog(@"%@",_url);
        NSMutableURLRequest *request =[[NSMutableURLRequest alloc] init];
        [request setURL:[NSURL URLWithString:_url]];
        [request setHTTPMethod:@"GET"];
        //-- Getting response form server
        NSError *error = nil;
        NSURLResponse *response;
        WebRequest *req = [[WebRequest alloc] init];
        NSData *responseData = [req sendSynchronousRequest:request returningResponse:&response error:&error];
        if (error)
        {
            qlerror(@"%@",error.localizedDescription);
            [progressBar stopAnimation:progressBar];
            [agentConfigImage setImage:[NSImage imageNamed:@"NoIcon"]];
            [uploadButton setEnabled:YES];
            [progressBar stopAnimation:progressBar];
            return;
        }
        
        //int httpcode = (int)[(NSHTTPURLResponse *)response statusCode];
        if (req.httpStatusCode == 424)
        {
            _authToken = nil;
            [self uploadPackage:nil];
            return;
        }
        
        NSError *bErr = nil;
        NSDictionary *json = [NSJSONSerialization JSONObjectWithData:responseData options:0 error:&bErr];
        if (bErr) {
            [agentConfigImage setImage:[NSImage imageNamed:@"NoIcon"]];
            [uploadButton setEnabled:YES];
            [progressBar stopAnimation:progressBar];
            return;
        }
        [agentConfigImage setImage:[NSImage imageNamed:@"YesIcon"]];
        result = [[json objectForKey:@"result"] objectForKey:@"plist"];
        
        // Write the Servers Pub key to base.pkg
        [self writeServerPubKey:[[json objectForKey:@"result"] objectForKey:@"pubKey"]
                           hash:[[json objectForKey:@"result"] objectForKey:@"pubKeyHash"]];
        
        
        NSArray *pkgs1;
        
        bErr = nil;
        [writeConfigImage setImage:[NSImage imageNamed:NSImageNameRemoveTemplate]];
        [writeConfigImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        pkgs1 = [self writePlistForPackage:result error:&bErr];
        if (bErr) {
            [writeConfigImage setImage:[NSImage imageNamed:@"NoIcon"]];
            [uploadButton setEnabled:YES];
            [progressBar stopAnimation:progressBar];
            return;
        } else {
            [writeConfigImage setImage:[NSImage imageNamed:@"YesIcon"]];
        }
        [writeConfigImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        
        NSArray *pkgs2;
        bErr = nil;
        [flattenPackagesImage setImage:[NSImage imageNamed:NSImageNameRemoveTemplate]];
        [flattenPackagesImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        pkgs2 = [self flattenPackages:pkgs1 error:&bErr];
        if (bErr) {
            [flattenPackagesImage setImage:[NSImage imageNamed:@"NoIcon"]];
            [uploadButton setEnabled:YES];
            [progressBar stopAnimation:progressBar];
            return;
        } else {
            [flattenPackagesImage setImage:[NSImage imageNamed:@"YesIcon"]];
        }
        [flattenPackagesImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        
        NSArray *pkgs3;
        bErr = nil;
        [compressPackgesImage setImage:[NSImage imageNamed:NSImageNameRemoveTemplate]];
        [compressPackgesImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        pkgs3 = [self compressPackages:pkgs2 error:&bErr];
        if (bErr) {
            [compressPackgesImage setImage:[NSImage imageNamed:@"NoIcon"]];
            [uploadButton setEnabled:YES];
            [progressBar stopAnimation:progressBar];
            return;
        } else {
            [compressPackgesImage setImage:[NSImage imageNamed:@"YesIcon"]];
        }
        [compressPackgesImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
        
        d = [NSUserDefaults standardUserDefaults];
        if ([d objectForKey:@"dDoNotUpload"]) {
            if ([[d objectForKey:@"dDoNotUpload"] integerValue] == 1)
            {
                NSString *p = [[pkgs3 objectAtIndex:0] stringByDeletingLastPathComponent];
                [[NSWorkspace sharedWorkspace] openFile:p];
                [progressBar stopAnimation:progressBar];
                [uploadButton setEnabled:YES];
                return;
            }
        } else {
            [postPackagesImage setImage:[NSImage imageNamed:NSImageNameRemoveTemplate]];
            [postPackagesImage performSelectorOnMainThread:@selector(needsDisplay) withObject:nil waitUntilDone:YES];
            [self postFilesREST:(NSArray *)pkgs3];
            
            [progressBar stopAnimation:progressBar];
            [uploadButton setEnabled:YES];
        }
    }
}

- (NSDictionary *)agentPKGData:(NSString *)package
{
    // Used By the postFilesREST method
    //
    
    MPCrypto *mpc = [[MPCrypto alloc] init];
    NSMutableDictionary *d;
    NSString *pkgName;
    NSDictionary *confDict;
    
    pkgName = [[package lastPathComponent] stringByDeletingPathExtension];
    d = [[NSMutableDictionary alloc] init];
    
    [d setObject:pkgName forKey:@"pkg_name"];
    if ([pkgName isEqualToString:@"Base.pkg"]) {
        [d setObject:@"app" forKey:@"type"];
        confDict = [NSDictionary dictionaryWithDictionary:_agentDict];
    } else if ([pkgName isEqualToString:@"Updater.pkg"]) {
        [d setObject:@"update" forKey:@"type"];
        confDict = [NSDictionary dictionaryWithDictionary:_updaterDict];
    }
    [d setObject:[confDict objectForKey:@"agent_ver"] forKey:@"agent_ver"];
    [d setObject:[confDict objectForKey:@"ver"] forKey:@"version"];
    [d setObject:[confDict objectForKey:@"build"] forKey:@"build"];
    [d setObject:[mpc sha1HashForFile:package] forKey:@"pkg_hash"];
    [d setObject:[confDict objectForKey:@"osver"] forKey:@"osver"];
    
    return (NSDictionary *)d;
}

- (BOOL)writeServerPubKey:(NSString *)aKey hash:(NSString *)aKeyHash
{
    NSArray *dirFiles = [fm contentsOfDirectoryAtPath:[_tmpDir stringByAppendingPathComponent:@"MPClientInstall"] error:nil];
    NSArray *pkgFiles = [dirFiles filteredArrayUsingPredicate:[NSPredicate  predicateWithFormat:@"self ENDSWITH '.pkg'"]];
    NSString *fullPathSrvKey;
    NSString *fullPathPKG;
    for (NSString *pkg in pkgFiles)
    {
        fullPathPKG = [[_tmpDir stringByAppendingPathComponent:@"MPClientInstall"] stringByAppendingPathComponent:pkg];
        if ([[pkg lastPathComponent] isEqualToString:@"Base.pkg"]) {
            if ([fm fileExistsAtPath:[fullPathPKG stringByAppendingPathComponent:@"Scripts"]])
            {
                fullPathSrvKey = [fullPathPKG stringByAppendingPathComponent:@"Scripts/ServerPub.pem"];
                [aKey writeToFile:fullPathSrvKey atomically:NO encoding:NSUTF8StringEncoding error:NULL];
                if ([[[self md5Hash:fullPathSrvKey] lowercaseString] isEqualToString:aKeyHash.lowercaseString] ) {
                    return YES;
                } else {
                    return NO;
                }
            }
        }
    }
    
    return NO;
}

- (NSString*)md5Hash:(NSString *)filePath
{
    // Create pointer to the string as UTF8
    const char *ptr = [filePath UTF8String];
    
    // Create byte array of unsigned chars
    unsigned char md5Buffer[CC_MD5_DIGEST_LENGTH];
    
    // Create 16 byte MD5 hash value, store in buffer
    CC_MD5(ptr, strlen(ptr), md5Buffer);
    
    // Convert MD5 value in the buffer to NSString of hex values
    NSMutableString *output = [NSMutableString stringWithCapacity:CC_MD5_DIGEST_LENGTH * 2];
    for(int i = 0; i < CC_MD5_DIGEST_LENGTH; i++)
        [output appendFormat:@"%02x",md5Buffer[i]];
    
    return output;
}

@end
