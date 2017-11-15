// Copyright (C) ABBYY (BIT Software), 1993 - 2012. All rights reserved.

#import "MIOperationListener.h"

NSString* const ListenerLogFileName = @"Results.txt";

//----------------------------------------------------------------------------------------------------------------------

@implementation MIOperationListener

+ (id)listenerForOperation:(MIFineOperation)operationIndex
{
	// create and initialize new operation listener
	switch( operationIndex ) {
		case FO_DetectBlur:
			return [[MIDetectBlurListener alloc] init];
		case FO_DetectGlare:
			return [[MIDetectGlareListener alloc] init];
		case FO_DetectNoise:
			return [[MIDetectNoiseListener alloc] init];
		default:
			return nil;
	}
}

@synthesize imageOrientation;
@synthesize imageSize;
@synthesize operationResult;

- (void)dealloc
{
	self.operationResult = nil;
}

- (id)adjustResult:(id)result
{
	return result;
}

- (NSFileHandle*)logFile
{
	NSString* logFilePath = [[NSSearchPathForDirectoriesInDomains( NSDocumentDirectory, NSUserDomainMask, YES ) lastObject]
		stringByAppendingPathComponent:ListenerLogFileName];
	NSFileHandle* logFile = [NSFileHandle fileHandleForWritingAtPath:logFilePath];
	if( logFile == nil ) {
		[[NSFileManager defaultManager] createFileAtPath:logFilePath contents:nil attributes:nil];
		logFile = [NSFileHandle fileHandleForWritingAtPath:logFilePath];
	}
	[logFile truncateFileAtOffset:[logFile seekToEndOfFile]];
	return logFile;
}

- (NSString*)timestampWithTime:(NSDate*)date
{
	return [NSDateFormatter localizedStringFromDate:date
		dateStyle:NSDateFormatterShortStyle timeStyle:NSDateFormatterMediumStyle];
}

- (NSString*)operationName
{
	return @"GenericOperation";
}

- (NSMutableDictionary*)dictionaryResult
{
    return nil;
}

- (NSString*)readableResult
{
	return [NSString stringWithFormat:@"%@", self.operationResult];
}

- (NSString*)operationLogWithTime:(NSDate*)date
{
	return [NSString stringWithFormat:@"[%@, %@: %@]\r\n",
		[self timestampWithTime:date], [self operationName], [self readableResult]];
}

- (void)onProgressFinished:(id)result
{
    @autoreleasepool {
        // the operation has finished successfully, and we're here on a worker thread ready to obtain results
        self.operationResult = [self adjustResult:result];
        // append the data to the log file
        NSString* logString = [self operationLogWithTime:[NSDate date]];
        [[self logFile] writeData:[logString dataUsingEncoding:NSUTF8StringEncoding]];
    }
}

@end

//----------------------------------------------------------------------------------------------------------------------

@implementation MIDetectBlurListener

- (NSString*)operationName
{
	return @"DetectBlur";
}

- (NSString*)readableResult
{
    MIBlurInfo* info = (MIBlurInfo*)self.operationResult;
	NSMutableString* resultString = [NSMutableString
		stringWithFormat:@"isDetected=%i; undefinedSize=%f; examinedSize=%f; motionBlurSize=%f; defocusSize=%f",
		info.isDetected, info.undefinedSize, info.examinedSize, info.motionBlurSize, info.defocusSize];
	[resultString appendString:@"; blurredBlocks={ "];
	for( MIRect* block in info.blurredBlocks ) {
		[resultString appendFormat:@"(%f, %f)-(%f, %f) ", block.origin.x, block.origin.y,
			block.origin.x + block.size.width, block.origin.y + block.size.height];
	}
	[resultString appendString:@"}; defocusedBlocks={ "];
	for( MIRect* block in info.defocusedBlocks ) {
		[resultString appendFormat:@"(%f, %f)-(%f, %f) ", block.origin.x, block.origin.y,
			block.origin.x + block.size.width, block.origin.y + block.size.height];
	}
	[resultString appendString:@"}"];
	return resultString;
}

- (NSMutableDictionary*)dictionaryResult
{
    NSMutableDictionary* result;
    MIBlurInfo* info = (MIBlurInfo*)self.operationResult;
    result = [NSMutableDictionary new];
    result[@"isDetected"] = [NSString stringWithFormat:@"%d", info.isDetected];
    result[@"undefinedSize"] = [NSString stringWithFormat:@"%f", info.undefinedSize];
    result[@"examinedSize"] = [NSString stringWithFormat:@"%f", info.examinedSize];
    result[@"motionBlurSize"] = [NSString stringWithFormat:@"%f", info.motionBlurSize];
    result[@"blurredBlocks"] = [NSString stringWithFormat:@"%lu", (unsigned long)info.blurredBlocks.count];
    result[@"defocusBlocks"] = [NSString stringWithFormat:@"%lu", (unsigned long)info.defocusedBlocks.count];
    return result;
}

@end

//----------------------------------------------------------------------------------------------------------------------

@implementation MIDetectGlareListener

- (NSString*)operationName
{
	return @"DetectGlare";
}

- (NSMutableDictionary*)dictionaryResult
{
    NSMutableDictionary* result;
    MIGlareInfo* info = (MIGlareInfo*)self.operationResult;
    result = [NSMutableDictionary new];
    result[@"isDetected"] = [NSString stringWithFormat:@"%d", info.isDetected];
    result[@"mu02"] = [NSString stringWithFormat:@"%f", info.mu02];
    result[@"mu11"] = [NSString stringWithFormat:@"%f", info.mu11];
    result[@"mu20"] = [NSString stringWithFormat:@"%f", info.mu20];
    result[@"x"] = [NSString stringWithFormat:@"%f", info.spotCenter.x];
    result[@"y"] = [NSString stringWithFormat:@"%f", info.spotCenter.y];
    result[@"optimalBinarizationThreshold"] = [NSString stringWithFormat:@"%d", info.optimalBinarizationThreshold];
    return result;
}

- (NSString*)readableResult
{
	MIGlareInfo* info = (MIGlareInfo*)self.operationResult;
	NSString* resultString = [NSString
		stringWithFormat:@"isDetected=%i; mu02=%f; mu11=%f; mu20=%f; spotCenter=(%f, %f); optimalBinarizationThreshold=%i",
		info.isDetected, info.mu02, info.mu11, info.mu20, info.spotCenter.x, info.spotCenter.y,
		info.optimalBinarizationThreshold];
	return resultString;
}

@end

//----------------------------------------------------------------------------------------------------------------------

@implementation MIDetectNoiseListener

- (NSString*)operationName
{
	return @"DetectNoise";
}

- (NSMutableDictionary*)dictionaryResult
{
    NSMutableDictionary* result;
    MINoiseInfo* info = (MINoiseInfo*)self.operationResult;
    result = [NSMutableDictionary new];
    result[@"isHigh"] = [NSString stringWithFormat:@"%d", info.isHigh];
    result[@"signalToNoiseRatio"] = [NSString stringWithFormat:@"%f", info.signalToNoiseRatio];
    return result;
}

- (NSString*)readableResult
{
	MINoiseInfo* info = (MINoiseInfo*)self.operationResult;
	NSString* resultString = [NSString stringWithFormat:@"isHigh=%i; signalToNoiseRatio=%f",
		info.isHigh, info.signalToNoiseRatio];
	return resultString;
}

@end
