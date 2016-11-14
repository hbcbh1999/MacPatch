//
//     Generated by class-dump 3.5 (64 bit).
//
//     class-dump is Copyright (C) 1997-1998, 2000-2001, 2004-2013 by Steve Nygard.
//

@class NSArray, NSDictionary, SSDownload;

@interface SSPurchaseResponse : NSObject <NSSecureCoding>
{
    NSArray *_downloads;
    NSDictionary *_rawResponse;
    NSDictionary *_metrics;
}

+ (BOOL)supportsSecureCoding;
@property(retain) NSDictionary *metrics; // @synthesize metrics=_metrics;
@property(retain) NSArray<SSDownload*> *downloads; // @synthesize downloads=_downloads;
//- (void).cxx_destruct;
- (id)initWithCoder:(id)arg1;
- (void)encodeWithCoder:(id)arg1;
- (id)_newDownloadsFromItems:(id)arg1 withDSID:(id)arg2;
- (id)initWithDictionary:(id)arg1 userIdentifier:(id)arg2;

@end

