// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

// Automatically removes background elements, such as texture, dots, lines, and etc. This interface extends the FineOperation interface
@interface FineCleanBackground : FineOperation

// Creates the FineCleanBackground object given input parameters
// Parameters:
// details - Per mille of text in document that should be removed. The value should be in the range from 1 to 1000.
// 		The recommended value is 125. If this parameter is 0, the automatic detection is applied
+ (id)fineCleanBackgroundWithDetails:(int)details;

// Per mille of text in document that should be removed 
@property( nonatomic ) int details;

// Initializes the object with given parameters
// Parameters:
// details - Per mille of text in document that should be removed. The value should be in the range from 1 to 1000.
// 		The recommended value is 125. If this parameter is 0, the automatic detection is applied
- (id)initWithDetails:(int)details;

@end
