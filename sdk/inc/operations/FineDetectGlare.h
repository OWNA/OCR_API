// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineResultOperation.h"

@class MIGlareInfo;
@protocol MIListener;

//----------------------------------------------------------------------------------------------------------------------

// Detects the glare spot. This interface extends the FineResultOperation interface
@interface FineDetectGlare : FineResultOperation

// Creates the FineDetectBlur object given input parameters
// Parameters:
// listener - The listener object that contains the results of detection
// isGreyscale - Specifies whether the image is in grey scale already to avoid unnecessary conversion
// isFast - If YES, the detection is performed faster
+ (id)fineDetectGlareWithListener:(id<MIListener>)listener greyscale:(BOOL)isGreyscale mode:(BOOL)isFast;

// Specifies whether the image is in grey scale already to avoid unnecessary conversion 
@property( nonatomic, getter = isGreyscale ) BOOL greyscale;
// Processing mode flag
@property( nonatomic, getter = isFast ) BOOL fast;

// Initializes the object with given parameters
// Parameters:
// listener - The listener object that contains the results of detection
// isGreyscale - Specifies whether the image is in grey scale already to avoid unnecessary conversion
// isFast - If YES, the detection is performed faster
- (id)initWithListener:(id<MIListener>)listener greyscale:(BOOL)isGreyscale mode:(BOOL)isFast;

@end
