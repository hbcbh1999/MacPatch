//
//  MPOSUpgrade.m
/*
 Copyright (c) 2015, Lawrence Livermore National Security, LLC.
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

#import "MPOSUpgrade.h"

static NSString *migrationFile = @"/Users/Shared/.migrationid";

@interface MPOSUpgrade()

- (int)writeMigrationDataToDisk:(NSString *)aID label:(NSString *)aLabel migrationIDFile:(NSString *)aFilePath;

@end

@implementation MPOSUpgrade

- (int)postOSUpgradeStatus:(NSString *)action label:(NSString *)aLabel upgradeID:(NSString *)aUpgradeID error:(NSError **)error
{
    int result = 0;
    NSError *err = nil;
    MPWebServices *mpws = [[MPWebServices alloc] init];
    if ([[action lowercaseString] isEqualToString:@"start"] || [[action lowercaseString] isEqualToString:@"stop"])
    {
        NSString *resStr;
        resStr = [mpws postOSMigrationStatus:action label:aLabel migrationID:aUpgradeID error:&err];
        if (err) {
            if (error != NULL) *error = err;
            logit(lcl_vError,@"Error posting upgrade status.")
            logit(lcl_vError,@"%@",err.localizedDescription);
            result = 1;
        } else {
            logit(lcl_vInfo,@"Posting upgrade status for %@ was successful.",action);
            if ([[action lowercaseString] isEqualToString:@"start"]) {
                result = [self writeMigrationDataToDisk:aUpgradeID label:aLabel migrationIDFile:migrationFile];
            }
        }
    } else {
        NSDictionary *userInfo = @{ NSLocalizedDescriptionKey: NSLocalizedString(@"Action type not supported.", nil) };
        err = [NSError errorWithDomain:@"MPOSUpgradeError" code:-1001 userInfo:userInfo];
        if (error != NULL) *error = err;
        return 1;
    }

    return result;
}

- (int)writeMigrationDataToDisk:(NSString *)aID label:(NSString *)aLabel migrationIDFile:(NSString *)aFilePath
{
    NSError *err = nil;
    NSFileManager *fm = [NSFileManager defaultManager];
    NSString *parentDir = [aFilePath stringByDeletingLastPathComponent];
    BOOL isDir;
    BOOL exists = [fm fileExistsAtPath:parentDir isDirectory:&isDir];
    if (!exists)
    {
        [fm createDirectoryAtPath:parentDir withIntermediateDirectories:YES attributes:nil error:&err];
        if (err) {
            logit(lcl_vError,@"Error creating directory (%@).", parentDir);
            logit(lcl_vError,@"%@",err.localizedDescription);
            return 1;
        }
    } else {
        if (!isDir) {
            logit(lcl_vError,@"Error directory (%@) is a file.", parentDir);
            logit(lcl_vError,@"%@",err.localizedDescription);
            return 1;
        }
    }
    NSString *fileData = [NSString stringWithFormat:@"%@\n%@",aID,aLabel];
    err = nil;
    [fileData writeToFile:@"migrationFile" atomically:NO encoding:NSUTF8StringEncoding error:&err];
    if (err) {
        logit(lcl_vError,@"Error creating migration id file (%@).", migrationFile);
        logit(lcl_vError,@"%@",err.localizedDescription);
        return 1;
    }
    
    return 0;
}

@end
