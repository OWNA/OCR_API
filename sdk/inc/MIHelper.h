// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "MIErrors.h"

@class MIImage;
@class MISize;

//----------------------------------------------------------------------------------------------------------------------

// The image data manager
@interface MIHelper : NSObject

// Loads image data from buffer
// Parameters:
// buffer - An input buffer; pixels in the buffer must represent an ARGB_8888 image
// bufferSize - The size of the input buffer
// imageSize - The size of the image to load
// image - The loaded image
+ (MIExecutionResult)readFromBuffer:(const void*)buffer bufferSize:(int)bufferSize imageSize:(MISize*)imageSize
	image:(MIImage**)image;

// Stores ARGB_8888-formatted image data to buffer
// Parameters:
// image - An image to save
// buffer - An output buffer
// bufferSize - The size of the input buffer
+ (MIExecutionResult)writeToBuffer:(MIImage*)image buffer:(void*)buffer bufferSize:(int)bufferSize;

// Prepares for the sequential reading of the image
// Parameters:
// imageSize - size of the image to load
- (MIExecutionResult)startReadingFromBuffer:(MISize*)imageSize;

// Appends a portion of the image from the buffer
// Parameters:
// buffer - An input buffer; pixels in the buffer must represent an ARGB_8888 image
// bufferSize - The size of the input buffer
- (MIExecutionResult)readPortionFromBuffer:(const void*)buffer bufferSize:(int)bufferSize;

// Finishes the sequential reading of the image
// Parameters:
// image - The loaded image
- (MIExecutionResult)finishReadingFromBuffer:(MIImage**)image;

// Prepares for the sequential writing of the image
// Parameters:
// image - An image to write
- (MIExecutionResult)startWritingToBuffer:(MIImage*)image;

// Writes an ARGB_8888-formatted portion of the image to buffer
// Parameters:
// buffer - An output buffer
// bufferSize - The size of the output buffer
- (MIExecutionResult)writePortionToBuffer:(void*)buffer bufferSize:(int)bufferSize;

// Finishes sequential writing of the image
- (MIExecutionResult)finishWritingToBuffer;

@end
