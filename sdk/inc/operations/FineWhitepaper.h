// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

// Makes the whole document background white. This class extends the FineOperation class
@interface FineWhitepaper : FineOperation

// Creates the FineWhitepaper object given input parameters
// Parameters:
// radius - The smoothing radius as percent of the image size. The value should be positive. 
//	 	The recommended value is 50.
// strength - The strength of the brightness of the image. The higher value, the brighter image. 
// 		The value should be positive. The recommended value is 25.
// isFast - If YES, the conversion is performed faster
+ (id)fineWhitepaperWithRadius:(int)radius strength:(int)strength mode:(BOOL)isFast;

// The smoothing radius 
@property( nonatomic ) int radius;
// The filtering strength 
@property( nonatomic ) int strength;
// Processing mode flag
@property( nonatomic, getter = isFast ) BOOL fast;

// Initializes the object with given parameters
// Parameters:
// radius - The smoothing radius as percent of the image size. The value should be positive. 
//	 	The recommended value is 50.
// strength - The strength of the brightness of the image. The higher value, the brighter image. 
// 		The value should be positive. The recommended value is 25.
// isFast - If YES, the conversion is performed faster
- (id)initWithRadius:(int)radius strength:(int)strength mode:(BOOL)isFast;

@end
