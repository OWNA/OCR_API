// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

@class MISize;

//----------------------------------------------------------------------------------------------------------------------

// Represents an image
@interface MIImage : NSObject <NSCopying>

// Returns a copy of the MIImage object
// Parameters:
// other - A pointer to the MIImage object containing the image
+ (id)imageWithMIImage:(MIImage*)other;
// Returns the MIImage object created from an input Core Graphics object
// Parameters:
// image - The CGImageRef object containing an image
+ (id)imageWithCGImage:(CGImageRef)image;

// A pointer to the MISize object containing the image size
@property( nonatomic, readonly ) MISize* size;

// Initializes the MIImage object with an empty image
- (id)init;
// Initializes the MIImage object with another MIImage object
// Parameters:
// other - A poiter to the MIImage object containing the image
- (id)initWithMIImage:(MIImage*)other;
// Initializes the MIImage object with an input Core Graphics object
// Parameters:
// image - The CGImageRef object containing an image
- (id)initWithCGImage:(CGImageRef)image;

// Does the source image have compatible parameters of Alpha Channel - CGImageAlphaInfo.
// The problem is that kCGImageAlphaLast and kCGImageAlphaFirst are not supported.
+ (BOOL)isCompatibleCGImage:(CGImageRef)srcImage;

// Create the copy of source image which has compatible parameters of Alpha Channel - CGImageAlphaInfo.
// The problem is that kCGImageAlphaLast and kCGImageAlphaFirst are not supported.
+ (CGImageRef)createCompalibleCGImage:(CGImageRef)srcImage;

// Converts the MIImage object to the Core Graphics object
// The result must be released
- (CGImageRef)createCGImage;

@end
