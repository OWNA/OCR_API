// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

// Automatically removes noise from the image. This interface extends the FineOperation interface
@interface FineDenoiseS : FineOperation

// Creates the FineDenoiseS object given input parameters
// Parameters:
// amount - The amount of remaining details on the image. A value is in the range from 0 to 1. The default value is 0.5.
// isFast - If YES, the conversion is performed faster
+ (id)fineDenoiseSWithAmount:(float)amount mode:(BOOL)isFast;

// The amount of remaining details on the image
@property( nonatomic ) float amount;
// Processing mode flag
@property( nonatomic, getter = isFast ) BOOL fast;

// Initializes the object with given parameters
// Parameters:
// amount - The amount of remaining details on the image. A value is in the range from 0 to 1. The default value is 0.5.
// isFast - If YES, the conversion is performed faster
- (id)initWithAmount:(float)amount mode:(BOOL)isFast;

@end
