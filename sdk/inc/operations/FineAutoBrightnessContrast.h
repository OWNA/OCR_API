// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

// Automatically adjusts brightness and contrast of the image. This interface extends the FineOperation interface
@interface FineAutoBrightnessContrast : FineOperation

// Creates the FineAutoBrightnessContrast object given brightness and contrast.
// Parameters:
// brightness - A coefficient for automatic brightness correction. The value should be in the range from 0 to 1.
// 		The recommended value is 0.05. If this parameter is 0, the brightness is not adjusted.
// contrast - A coefficient for automatic contract correction. The value should be in the range from 0 to 1.
// 		The recommended value is 0.03. If this parameter is 0, the contrast is not adjusted.
+ (id)fineAutoBrightnessContrastWithBrightness:(float)brightness contrast:(float)contrast;

// A coefficient for automatic brightness correction
@property( nonatomic ) float brightness;
// A coefficient for automatic brightness correction
@property( nonatomic ) float contrast;

// Initializes the object with given parameters
// Parameters:
// brightness - A coefficient for automatic brightness correction. The value should be in the range from 0 to 1.
// 		The recommended value is 0.05. If this parameter is 0, the brightness is not adjusted.
// contrast - A coefficient for automatic contract correction. The value should be in the range from 0 to 1.
// 		The recommended value is 0.03. If this parameter is 0, the contrast is not adjusted.
- (id)initWithBrightness:(float)brightness contrast:(float)contrast;

@end
