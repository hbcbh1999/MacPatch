//
//  MPAppController.h
/*
 Copyright (c) 2017, Lawrence Livermore National Security, LLC.
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

#import <Cocoa/Cocoa.h>

@class ClientCheckInOperation;
@class AgentScanAndUpdateOperation;
@class AntiVirusScanAndUpdateOperation;
@class InventoryOperation;
@class PatchScanAndUpdateOperation;
@class MPSWDistTaskOperation;
@class Profiles;
@class GetServerListOperation;
@class PostFailedWSRequests;
@class GetASUSListOperation;

@interface MPAppController : NSObject {
    
@private
    MPAgent *si;
	NSOperationQueue *queue;
	
	ClientCheckInOperation *clientOp;
	AgentScanAndUpdateOperation *agentOp;
	AntiVirusScanAndUpdateOperation *avOp;
	InventoryOperation *invOp;
	PatchScanAndUpdateOperation *patchOp;
    MPSWDistTaskOperation *swDistOp;
    Profiles *profilesOp;
    GetServerListOperation *serverListOp;
	PostFailedWSRequests *postFailedWSRequestsOp;
    GetASUSListOperation *suServerListOp;

	BOOL useOperationQueue;
}

@property (nonatomic, assign) BOOL useOperationQueue;

- (void)runWithType:(int)aArg;
- (void)runAsDaemon;
- (void)watchTasksPlistForChangesMethod;
- (void)runTasksLoop;

- (void)runClientCheckIn;
- (void)runInventoryCollection;
- (void)runPatchScan;
- (void)runPatchScanAndUpdate;
- (void)runAVInfoScan;
- (void)runAVInfoScanAndDefsUpdate;
- (void)scanAndUpdateAgentUpdater;
- (void)runSWDistScanAndInstall;
- (void)runProfilesScanAndInstall;
- (void)runGetServerListOperation;
- (void)runPostFailedWSRequests;

@end
