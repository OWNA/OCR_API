// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineResultOperation.h"

@class MIQuad;
@protocol MIListener;

//----------------------------------------------------------------------------------------------------------------------

// Recognizes edges of a paper sheet on the image as a quadrangle. This interface extends the FineResultOperation interface
@interface FineRecognizeEdges : FineResultOperation

// Creates the FineRecognizeEdges object given input parameters
// Parameters:
// listener - The listener object that contains the results of the edge recognition
// isGreyscale - Specifies whether the image is in grey scale already to avoid unnecessary conversion
// isFast - If YES, the detection is performed faster
+ (id)fineRecognizeEdgesWithListener:(id<MIListener>)listener greyscale:(BOOL)isGreyscale mode:(BOOL)isFast;

// Specifies whether the image is in grey scale already to avoid unnecessary conversion
@property( nonatomic, getter = isGreyscale ) BOOL greyscale;
// Processing mode flag
@property( nonatomic, getter = isFast ) BOOL fast;

// Initializes the object with given parameters
// Parameters:
// listener - The listener object that contains the results of the edge recognition
// isGreyscale - Specifies whether the image is in grey scale already to avoid unnecessary conversion
// isFast - If YES, the detection is performed faster
- (id)initWithListener:(id<MIListener>)listener greyscale:(BOOL)isGreyscale mode:(BOOL)isFast;

@end
