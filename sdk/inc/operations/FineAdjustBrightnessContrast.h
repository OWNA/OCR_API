// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

// Adjust contrast/brightness on the image. This interface extends the FineOperation interface	
@interface FineAdjustBrightnessContrast : FineOperation

// Creates the FineAdjustBrightnessContrast object given brightness and contrast.
// Parameters:
// brightness - The value of brigthness should be in the range from 0 to 1. The default value is 0.5.
// contrast - The value of contrast should be in the range from 0 to 1. The default value is 0.5.
+ (id)fineAdjustBrightnessContrastWithBrightness:(float)brightness contrast:(float)contrast;

// Brightness
@property( nonatomic ) float brightness;
// Contrast
@property( nonatomic ) float contrast;

// Initializes the object with given parameters
// Parameters:
// brightness - The value of brigthness should be in the range from 0 to 1. The default value is 0.5.
// contrast - The value of contrast should be in the range from 0 to 1. The default value is 0.5.
- (id)initWithBrightness:(float)brightness contrast:(float)contrast;

@end
