// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "MICallback.h"

@class MIImage;
@class MIGenericError;
@class FineOperation;
@protocol MIAsyncDelegate;

//----------------------------------------------------------------------------------------------------------------------

// The manager of the asynchronous image processing
@interface MIAsyncProcessor : NSOperation <MICallback>

// Creates the MIAsyncProcessor object given the the image and the delegate
// Parameters:
// image - The image
// delegate - The processing delegate
+ (id)asyncProcessorWithImage:(MIImage*)image delegate:(id<MIAsyncDelegate>)delegate;

// The image
@property( retain ) MIImage* image;
// A list of operations
@property( readonly ) NSArray* operationsList;
// The processing delegate
@property( assign ) id<MIAsyncDelegate> delegate;

// Creates the MIAsyncProcessor object given the the image and the delegate
// Parameters:
// image - The image
// delegate - The processing delegate
- (id)initWithImage:(MIImage*)image delegate:(id<MIAsyncDelegate>)delegate;

// Executes operations asynchronously in the specified order. It returns a pointer to the NSOperationQueue object with the created queue
// Parameters:
// operations - A list of operations to execute
- (NSOperationQueue*)execute:(NSArray*)operations;
//- (NSOperationQueue*)execute:(FineOperation*)firstOperation, ... NS_REQUIRES_NIL_TERMINATION;

// Executes operations asynchronously in the specified order in the existing queue
// Parameters:
// operations - A list of operations to execute
// queue - A pointer to the NSOperationQueue object where the operations are added
- (void)execute:(NSArray*)operations inQueue:(NSOperationQueue*)queue;
//- (void)execute:(FineOperation*)firstOperation, ... NS_REQUIRES_NIL_TERMINATION inQueue:(NSOperationQueue*)queue;

@end
