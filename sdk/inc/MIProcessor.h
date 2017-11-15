// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"
#import "MICallback.h"

// Represents a manager of the image processing. It extends the FineOperation class and implements the MICallback interface
@interface MIProcessor : FineOperation <MICallback>

// Creates the MIProcessor object given a list of operation to execute.
// Parameters:
// operations - A list of operations to execute
+ (id)processorWithOperations:(NSArray*)operations;

//  A list of operations
@property( retain ) NSArray* operations;

// Initialize with operations
// Parameters:
// operations - A list of operations to execute
- (id)initWithOperations:(NSArray*)operations;
//- (id)initWithOperations:(FineOperation*)firstOperation, ... NS_REQUIRES_NIL_TERMINATION;

@end
