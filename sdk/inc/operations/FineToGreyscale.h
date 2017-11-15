// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

// Converts the color RGB image to greyscale image that all RGB channels contain the same grey image. This interface extends the FineOperation interface
@interface FineToGreyscale : FineOperation

// Creates the FineToGreyscale object given the flag
// Parameters:
// isAutoInverted - Specifies whether the reversed image should be automatically inverted before the conversion
+ (id)fineToGreyscaleWithAutoInvert:(BOOL)isAutoInverted;

// Specifies whether the reversed image should be automatically inverted 
@property( nonatomic, getter = isAutoInverted ) BOOL autoInverted;

// Initializes the object with given parameters
// Parameters:
// isAutoInverted - Specifies whether the reversed image should be automatically inverted before the conversion
- (id)initWithAutoInvert:(BOOL)isAutoInverted;

@end
