// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"
#import "MITypes.h"

// Rotates the image to quarter angles. This interface extends the FineOperation interface
@interface FineRotateFixed : FineOperation

// Creates the FineRotate object given the rotation angle
// Parameters:
// angle - fixed image CCW rotation angle
+ (id)fineRotateFixedWithAngle:(MIFixedAngle)angle;

// The rotation angle specified by value from the MIFixedAngle enum 
@property( nonatomic ) MIFixedAngle angle;

// Initializes the object with given parameters
// Parameters:
// angle - fixed image CCW rotation angle
- (id)initWithAngle:(MIFixedAngle)angle;

@end
