// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

// Removes noise from binary document images. This interface extends the FineOperation interface
@interface FineHeavyCleanup : FineOperation

// Get initialized operation
+ (id)fineHeavyCleanupWithSize:(int)size threshold:(int)threshold;

// Filter size in pixels
@property( nonatomic ) int size;
// Filter threshold
@property( nonatomic ) int threshold;

// Initializes the object with given parameters
// Parameters:
// size - filter size in pixels, 35 is recommended value, recommended range is 10 - 100;
// higher values allow to remove more noise details but the text can be affected too
// threshold - filter threshold in levels, 10 is recommended value, recommended range is 1 - 30;
// higher values allow to remove more noise details but the text can be affected too
- (id)initWithSize:(int)size threshold:(int)threshold;

@end
