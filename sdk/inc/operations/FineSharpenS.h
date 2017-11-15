// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

// Sharpens the image. This interface extends the FineOperation interface
@interface FineSharpenS : FineOperation

// Get initialized operation
+ (id)fineSharpenSWithStrength:(int*)strength threshold:(int)threshold;

// Sharpening strength coefficients wrapped in NSData
@property( nonatomic, copy ) NSData* strength;
// Filter threshold
@property( nonatomic ) int threshold;

// Initializes the object with given parameters
// Parameters:
// strength - array of sharpening strength coefficients, from highest frequency to lowest (%, 0 - no sharpening)
// threshold - filter threshold (0 - 255)
- (id)initWithStrength:(int[5])strength threshold:(int)threshold;

@end
