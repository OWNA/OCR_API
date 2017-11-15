// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

// Rotates the image. This interface extends the FineOperation interface
@interface FineRotate : FineOperation

// Creates the FineRotate object given the rotation angle
// Parameters:
// angle - A float value of the rotation angle in radians. The rotation is made counterclockwise
+ (id)fineRotateWithAngle:(float)angle;

// The rotation angle in radians
@property( nonatomic ) float angle;

// Initializes the object with given parameters
// Parameters:
// angle - A float value of the rotation angle in radians. The rotation is made counterclockwise
- (id)initWithAngle:(float)angle;

@end
