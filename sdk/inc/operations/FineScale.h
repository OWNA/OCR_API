// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

@class MISize;

//----------------------------------------------------------------------------------------------------------------------

// Scales the image. This interface extends the FineOperation interface
@interface FineScale : FineOperation

// Creates the FineScale object given the size
// Parameters:
// size - The size of the resulting image 
+ (id)fineScaleWithSize:(MISize*)size;

// The size of the resulting image 
@property( nonatomic, copy ) MISize* size;

// Initializes the object with given parameters
// Parameters:
// size - The size of the resulting image 
- (id)initWithMISize:(MISize*)size;

@end
