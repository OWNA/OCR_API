// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

@class MIImage;
@class MIGenericError;
@protocol MICallback;
@protocol MIListener;

//----------------------------------------------------------------------------------------------------------------------

// An interface representing the results of image processing.
@interface FineResultOperation : FineOperation

// The MIListener object
@property( retain ) id<MIListener> listener;

// Creates the FineResultOperation object given the MIListener object
// Parameters:
// listener - The MIListener object that delivers the processing result
- (id)initWithListener:(id<MIListener>)listener;

// Processes an input image and returns the result
// Parameters:
// image - A pointer to the MIImage object containing the image
// callback - The MICallback object that receives information about the operation progress
// error - A pointer to the execution error pointer
- (id)processImageWithResult:(MIImage*)image callback:(id<MICallback>)callback error:(MIGenericError**)error;
	
@end
