// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

// Scales the image. This interface extends the FineOperation interface
@interface FineScaleFixed : FineOperation

// Creates the FineScaleFixed object given the scale
// Parameters:
// scale - The scale factor of axes. 0.01 is the minimum supported value.
+ (id)fineScaleFixedWithScale:(float)scale;

// The scale factor of axes
@property( nonatomic ) float scale;

// Initializes the object with given parameters
// Parameters:
// scale - The scale factor of axes. 0.01 is the minimum supported value.
- (id)initWithScale:(float)scale;

@end
