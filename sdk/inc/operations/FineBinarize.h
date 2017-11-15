// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

// Binarizes the image. This interface extends the FineOperation interface
@interface FineBinarize : FineOperation

// Creates the FineBinarize object given input parameters
// Parameters:
// isGreyscale - Specifies whether the image is in grey scale already to avoid unnecessary conversion
// whiteness - The level of the white color. A float value is in range from 0 to 1.0
+ (id)fineBinarizeWithGreyscale:(BOOL)isGreyscale whiteness:(float)whiteness;

// Specifies whether the image is in grey scale already to avoid unnecessary conversion
@property( nonatomic, getter = isGreyscale ) BOOL greyscale;
// The level of the white color
@property( nonatomic ) float whiteness;

// Initializes the object with given parameters
// Parameters:
// isGreyscale - Specifies whether the image is in grey scale already to avoid unnecessary conversion
// whiteness - The level of the white color. A float value is in range from 0 to 1.0
- (id)initWithGreyscale:(BOOL)isGreyscale whiteness:(float)whiteness;

@end
