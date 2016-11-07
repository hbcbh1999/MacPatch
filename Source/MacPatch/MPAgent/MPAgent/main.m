//
//  main.m
//  MPAgent
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

#import <Foundation/Foundation.h>
#import "MPAppController.h"
#import "MPAgentRegister.h"
#import "MPInv.h"
#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <unistd.h>
#include "MacPatch.h"

#define APPVERSION	@"2.2.0.0"
#define APPNAME		@"MPAgent"

#define NOREADKEYS     99996
#define NOREGKEY       99997
#define NOOPTPUB       99998
#define NOOPTPUBSTR    99999

void usage(void);

int main (int argc, char * argv[])
{
	@autoreleasepool
    {
        /*
        NSError *err = nil;
        NSString *srvPubKeyPath = @"/Library/MacPatch/Client/Data/server_pub.pem";
        //NSString *srvPubKeyData = [NSString stringWithContentsOfFile:srvPubKeyPath encoding:NSUTF8StringEncoding error:NULL];
        MPAgentRegister *ar = [[MPAgentRegister alloc] init];
        MPCrypto *mc = [[MPCrypto alloc] init];
        
        // First Add Server Public Key
        printf("Adding server public key via string.\n");
        if (![ar addServerPublicKeyFileToKeychain:srvPubKeyPath error:&err]) {
            printf("Add server public key string returned false.\n");
            if (err) {
                NSLog(@"%@",err.localizedDescription);
            }
            exit(1);
        }
        
        // Generate Registration Data
        err = nil;
        NSDictionary *d = [ar generateRegistrationPayload:&err];
        if (err) {
            NSLog(@"%@",err.localizedDescription);
        } else {
            NSLog(@"%@",d);
        }
        
        // Post Reg data to Web Service
        
        exit(0);
         */
        
        
		int a_Type = 99;
		BOOL echoToConsole = NO;
		BOOL debugLogging = NO;
		BOOL traceLogging = NO;
		BOOL verboseLogging = NO;
        BOOL doRegistration = NO;
        NSString *regKeyArg = @"999999999";
        NSString *regSrvPubKeyStr = @"NA";
        NSString *regSrvPubKeyPath = @"/tmp";
        // Inventory
        NSString *invArg = NULL;
		
		// Setup argument processing
		int c;
		while (1)
		{
			static struct option long_options[] =
			{
				{"Daemon"			,no_argument	    ,0, 'd'},
				{"Queue"			,no_argument	    ,0, 'q'},
				{"Debug"			,no_argument	    ,0, 'D'},
				{"Trace"			,no_argument	    ,0, 'T'},
				{"CheckIn"			,no_argument	    ,0, 'c'},
				{"Scan"				,no_argument	    ,0, 's'},
				{"Update"			,no_argument	    ,0, 'u'},
				{"Inventory"		,no_argument	    ,0, 'i'},
				{"AVInfo"			,no_argument	    ,0, 'a'},
				{"AVUpdate"			,no_argument	    ,0, 'U'},
				{"AgentUpdater"		,no_argument	    ,0, 'G'},
                {"SWScanUpdate" 	,no_argument	    ,0, 'S'},
                {"Profile"          ,no_argument	    ,0, 'p'},
                {"WebServicePost"   ,no_argument	    ,0, 'w'},
                {"Servers"          ,no_argument	    ,0, 'n'},
                {"SUServers"        ,no_argument	    ,0, 'z'},
				{"Echo"				,no_argument		,0, 'e'},
				{"Verbose"			,no_argument		,0, 'V'},
				{"version"			,no_argument		,0, 'v'},
				{"help"				,no_argument		,0, 'h'},
                
                // Inventory, not documented yet
                {"type"                 ,required_argument	,0, 't'},
                {"Audit"                ,no_argument		,0, 'A'},
                {"cuuid"                ,no_argument		,0, 'C'},
                
                // Registration
                {"register"             ,required_argument	,0, 'r'},       // Requires Server Supplied Regkey
                {"registerNoKey"        ,no_argument        ,0, NOREGKEY},  // Auto Register
                {"serverPubKeyFile"     ,required_argument	,0, NOOPTPUB},
                {"serverPubKeyString"   ,required_argument	,0, NOOPTPUBSTR},
                {"readClientKeys"       ,no_argument        ,0, NOREADKEYS},
				{0, 0, 0, 0}
			};
			// getopt_long stores the option index here.
			int option_index = 0;
			c = getopt_long (argc, argv, "dqDTcsuiaUGSpwnzeVvhr:t:AC", long_options, &option_index);
			
			// Detect the end of the options.
			if (c == -1)
				break;
			
			switch (c)
			{
                case NOOPTPUB:
                    NSLog(@"%@",[NSString stringWithUTF8String:optarg]);
                    regSrvPubKeyPath = [NSString stringWithUTF8String:optarg];
                    a_Type = 997;
                    break;
                    
                case NOOPTPUBSTR:
                    NSLog(@"%@",[NSString stringWithUTF8String:optarg]);
                    regSrvPubKeyStr = [NSString stringWithUTF8String:optarg];
                    a_Type = 998;
                    break;
                    
                case NOREGKEY:
                    a_Type = 999;
                    break;
                    
                case NOREADKEYS:
#if DEBUG
                    a_Type = 995;
#endif
                    break;
                    
				case 'd':
					a_Type = 99;
					break;
				case 'q':
					a_Type = 99;
					break;
				case 'c':
					a_Type = 1;
					break;
				case 'i':
					a_Type = 2;
					break;
                case 's':
					a_Type = 3;
					break;
				case 'u':
					a_Type = 4;
					break;
				case 'a':
					a_Type = 5;
					break;
				case 'U':
					a_Type = 6;
					break;
				case 'G':
					a_Type = 7;
					break;
                case 'S':
					a_Type = 8;
					break;
                case 'p':
					a_Type = 9;
					break;
                case 'n':
					a_Type = 10;
					break;
                case 'z':
                    a_Type = 13;
                    break;
                case 'w':
					a_Type = 11;
					break;
                // Inventory
                case 't':
                    invArg = [NSString stringWithUTF8String:optarg];
                    a_Type = 12;
                    break;
                case 'A':
                    invArg = @"Custom";
                    a_Type = 12;
                    break;
                case 'C':
                    printf("%s\n",[[MPSystemInfo clientUUID] UTF8String]);
                    return 0;
				case 'V':
					verboseLogging = YES;
					break;
				case 'D':
					verboseLogging = YES;
					break;
				case 'T':
					traceLogging = YES;
					break;
				case 'e':
					echoToConsole = YES;
					break;
				case 'v':
					printf("%s\n",[APPVERSION UTF8String]);
					return 0;
                case 'r':
                    a_Type = 996;
                    doRegistration = YES;
					regKeyArg = [NSString stringWithUTF8String:optarg];
					break;
				case 'h':
				case '?':
				default:
					usage();
			}
		}

        if (optind < argc) {
            while (optind < argc) {
                printf ("Invalid argument %s ", argv[optind++]);
            }
            usage();
            exit(0);
        }

		// Make sure the user is root or is using sudo
		if (getuid()) {
			printf("You must be root to run this app. Try using sudo.\n");
#if DEBUG
			printf("Running as debug...\n");
#else
			exit(0);
#endif
		}
        
        // Agent Registration
        if (a_Type == 999 || a_Type == 998 || a_Type == 997 || a_Type == 996 || a_Type == 995)
        {
            printf("Running client registration.\n");
            NSError *err = nil;
            MPKeychain *mpk;
            MPAgentRegister *mpar = [[MPAgentRegister alloc] init];
            if (a_Type == 999) {
                // Register using No Key
                NSError *err = nil;
                MPAgentRegister *mpar = [[MPAgentRegister alloc] init];
                mpar.overWriteKeyChainData = YES;
                NSDictionary *d = [mpar generateRegistrationPayload:&err];
                if (err) {
                    NSLog(@"%@",err.localizedDescription);
                } else {
                    NSLog(@"%@",d);
                }
                [mpar postRegistrationToServer:d];
            } else if (a_Type == 998) {
                // Server Pub Key String
                printf("Adding server public key via string.\n");
                if (![mpar addServerPublicKeyStringToKeychain:regSrvPubKeyStr error:&err]) {
                    printf("Add server public key string returned false.\n");
                    return 1;
                }
            } else if (a_Type == 997) {
                // Server Pub Key File
                printf("Adding server public key via file.\n");
                if (![mpar addServerPublicKeyFileToKeychain:regSrvPubKeyPath error:&err]) {
                    printf("Add server public key file returned false.\n");
                    return 1;
                }
            } else if (a_Type == 996) {
                // Register With Key
                
                
            } else if (a_Type == 995) {
                // Test Read Client Keys from Keychain
                mpk = [[MPKeychain alloc] init];
                NSDictionary *x = [mpk dictionaryFromKeychainWithKey:[mpk serviceLabelForClient] error:&err];
                if (!err) {
                    NSLog(@"%@",x);
                }
                NSDictionary *y = [mpk dictionaryFromKeychainWithKey:[mpk serviceLabelForServer] error:&err];
                if (!err) {
                    NSLog(@"%@",y);
                }

            } else {
                // No Key
                NSError *err = nil;
                MPAgentRegister *mpar = [[MPAgentRegister alloc] init];
                NSDictionary *d = [mpar generateRegistrationPayload:&err];
                if (err) {
                    NSLog(@"%@",err.localizedDescription);
                } else {
                    NSLog(@"%@",d);
                }
            }
            if (err) {
                printf("\n%s\n",[err.localizedDescription UTF8String]);
                return 1;
            }
            
            exit(0);
        }

    
        [[MPAgent sharedInstance] setG_agentVer:APPVERSION];
        [[MPAgent sharedInstance] setG_agentPid:[NSString stringWithFormat:@"%d",[[NSProcessInfo processInfo] processIdentifier]]];
        NSString *_logFile = [NSString stringWithFormat:@"%@/Logs/MPAgent.log",MP_ROOT_CLIENT];
		[MPLog setupLogging:_logFile level:lcl_vDebug];
		
		if ([[NSUserDefaults standardUserDefaults] boolForKey:@"MPAgentDebug"]) {
			debugLogging = YES;
		}
		
		if (verboseLogging || debugLogging) {
			lcl_configure_by_name("*", lcl_vDebug);
			if (verboseLogging) {
				[LCLLogFile setMirrorsToStdErr:YES];
			}
			logit(lcl_vInfo,@"***** %@ v.%@ started -- Debug Enabled *****", APPNAME, APPVERSION);
		} else if (traceLogging) {
			lcl_configure_by_name("*", lcl_vTrace);
			if (verboseLogging) {
				[LCLLogFile setMirrorsToStdErr:YES];
			}
			logit(lcl_vInfo,@"***** %@ v.%@ started -- Trace Enabled *****", APPNAME, APPVERSION);
		} else {
			lcl_configure_by_name("*", lcl_vInfo);
			if (echoToConsole) {
				[LCLLogFile setMirrorsToStdErr:YES];
			}
			logit(lcl_vInfo,@"***** %@ v.%@ started *****", APPNAME, APPVERSION);
		}
        
        // Process Inventory
        if (invArg !=NULL) {
            int x = 0;
            MPInv *inv = [[MPInv alloc] init];
            if ([invArg isEqual:@"Custom"]) {
                x = [inv collectAuditTypeData];
            } else if ([invArg isEqual:@"All"]) {
                x = [inv collectInventoryData];
            } else {
                x = [inv collectInventoryDataForType:invArg];
            }
            return x;
        }
        
        if (doRegistration) {
            int regResult = -1;
            NSString *clientKey = [[NSProcessInfo processInfo] globallyUniqueString];
            MPAgentRegister *mpar = [[MPAgentRegister alloc] init];
            regResult = [mpar registerClient:clientKey];
            // [mpar registerClient:regKeyArg hostName:[[MPAgent sharedInstance] g_hostName] clientKey:clientKey];
            // Hello
            NSLog(@"%d",regResult);
        } else {
            MPAppController *mpac = [[MPAppController alloc] initWithArg:a_Type];
            [[NSRunLoop currentRunLoop] run];
        }
		
    }
    return 0;
}

void usage(void) {
    
	printf("%s: MacPatch Agent\n",[APPNAME UTF8String]);
	printf("Version %s\n\n",[APPVERSION UTF8String]);
	printf("Usage: %s [OPTIONS]\n\n",[APPNAME UTF8String]);
	printf(" -d \tRun as background daemon.\n");
    printf(" -q \tRun as background daemon using operation queues.\n");
	printf(" -c \t --CheckIn \t\tRun client checkin.\n");
    printf(" -n \t --Servers \t\tRun server list verify/update.\n");
    printf(" -z \t --SUServers \t\tRun SUS server list verify/update.\n");
    printf(" -w \t --WebServicePost \tRe-post failed post attempts.\n\n");
    printf("Registration \n\n");
    
    printf("Inventory \n");
    printf("Option: -t [ALL] or [SPType]\n\n");
    printf(" -t\tInventory type, All is default.\n");
    printf(" \tSupported types:\n");
    printf(" \t\tAll\n");
    printf(" \t\tSPHardwareDataType\n");
    printf(" \t\tSPSoftwareDataType\n");
    printf(" \t\tSPNetworkDataType (Depricated)\n");
    printf(" \t\tSINetworkInfo\n");
    printf(" \t\tSPApplicationsDataType\n");
    printf(" \t\tSPFrameworksDataType\n");
    printf(" \t\tDirectoryServices\n");
    printf(" \t\tInternetPlugins\n");
    printf(" \t\tAppUsage\n");
    printf(" \t\tClientTasks\n");
    printf(" \t\tDiskInfo\n");
    printf(" \t\tUsers\n");
    printf(" \t\tGroups\n");
    printf(" \t\tFileVault\n");
    printf(" \t\tPowerManagment\n");
    printf(" \t\tBatteryInfo\n");
    printf(" \t\tConfigProfiles\n");
    printf(" \t\tAppStoreApps\n");
    printf(" \t\tMPServerList\n");
    printf(" \t\tPlugins\n");
    printf(" -A \tCollect Audit data.\n\n");
    printf(" -C \tDisplay client ID.\n");
	printf(" -e \t --Echo \t\t\tEcho logging data to console.\n");
	printf(" -V \tVerbose logging.\n");
	printf("\n -v \tDisplay version info. \n");
	printf("\n");
    exit(0);
}
