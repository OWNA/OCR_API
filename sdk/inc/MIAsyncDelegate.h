// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "MIErrors.h"

@class MIAsyncProcessor;

//----------------------------------------------------------------------------------------------------------------------

// The delegate protocol of asynchronous processing
@protocol MIAsyncDelegate <NSObject>

// Notifies the delegate about the processing progress
// Parameters:
// processor - A pointer to the MIAsyncProcessor object representing the manager of the asynchronous image processing
// index - The current operation index
// progress - The approximate percentage of image processing
- (void)onProcessingUpdated:(MIAsyncProcessor*)processor index:(int)index progress:(int)progress;

// Notifies the delegate about processing completion
// Parameters:
// processor - A pointer to the MIAsyncProcessor object representing the manager of the asynchronous image processing
// code - The result of execution
- (void)onProcessingFinished:(MIAsyncProcessor*)processor code:(MIExecutionResult)code;

@end
