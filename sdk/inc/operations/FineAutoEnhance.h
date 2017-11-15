// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

// Enhances local contrast and converts background to white (the output image is in grey scale). This interface extends the FineOperation interface
@interface FineAutoEnhance : FineOperation

// Get initialized operation
+ (id)fineAutoEnhanceWithDetails:(int)details noiseGap:(int)noiseGap mode:(BOOL)isFast;

// Radius of image details
@property( nonatomic ) int details;
// Maximum noise value
@property( nonatomic ) int noiseGap;
// Processing mode flag
@property( nonatomic, getter = isFast ) BOOL fast;

// Initializes the object with given parameters
// Parameters:
// details - The radius of image detail that should be removed as a percent of the image size. The value must be bigger than 0. 
// 		The recommended value is 15.
// noiseGap - The maximum level of noise in percent of the full dynamic range. The recommended value is 30.
// isFast - If YES, the conversion is performed faster
- (id)initWithDetails:(int)details noiseGap:(int)noiseGap mode:(BOOL)isFast;

@end
