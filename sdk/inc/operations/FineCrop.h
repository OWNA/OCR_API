// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

@class MIRect;

// Crops the image. This interface extends the FineOperation interface
@interface FineCrop : FineOperation

// Creates the FineCrop object given a rectangle
// Parameters:
// rect - An image rectangle to crop
+ (id)fineCropWithRect:(MIRect*)rect;

// An image rectangle to crop
@property( nonatomic, copy ) MIRect* rect;

// Initializes the object with given parameters
// Parameters:
// rect - An image rectangle to crop
- (id)initWithRect:(MIRect*)rect;

@end
