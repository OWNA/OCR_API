// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

@class MIImage;
@class MIGenericError;
@protocol MICallback;

//----------------------------------------------------------------------------------------------------------------------

// An interface for image processing routine
@interface FineOperation : NSObject

// Processes an input image
// Parameters:
// image - A pointer to the MIImage object containing the image
// callback - The MICallback object that receives information about the image processing progress
// error - A pointer to the execution error pointer
- (BOOL)processImage:(MIImage*)image callback:(id<MICallback>)callback error:(MIGenericError**)error;

@end
