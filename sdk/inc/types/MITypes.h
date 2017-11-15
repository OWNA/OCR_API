// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

// Describes the image channel
typedef enum MIImageChannelTag {
	IC_Hue, // The hue channel
	IC_Lightness, // The luminance channel
	IC_Saturation // The saturation channel
} MIImageChannel;

//----------------------------------------------------------------------------------------------------------------------

// Describes the image rotation angle
typedef enum MIFixedAngleTag {
	FA_0, // No rotation
	FA_90, // The image is rotated by 90 degrees clockwise
	FA_180, // The image is rotated by 180 degrees
	FA_270 // The image is rotated by 90 degrees counterclockwise
} MIFixedAngle;

//----------------------------------------------------------------------------------------------------------------------

// Represents the image size
@interface MISize : NSObject <NSCopying>

// Returns a copy of the MISize object
// Parameters:
// other - A poiter to the MISize object with the image size
+ (id)sizeWithMISize:(MISize*)other;
// Returns size initialized with width and height
// Parameters:
// width - A float value that specifies the image width
// height - A float value that specifies the image height
+ (id)sizeWithWidth:(float)width height:(float)height;
// Returns size initialized with the Core Graphics object
// Parameters:
// size - The CGSize object that specifies the image size
+ (id)sizeWithCGSize:(CGSize)size;

// The width of the image
@property( nonatomic ) float width;
// The height of the image
@property( nonatomic ) float height;

// Initializes the MISize object with another MISize object
// Parameters:
// other - A poiter to the MISize object with the image size
- (id)initWithMISize:(MISize*)other;
// Initializes with width and height
// Parameters:
// width - A float value that specifies the image width
// height - A float value that specifies the image height
- (id)initWithWidth:(float)width height:(float)height;
// Initializes with the Core Graphics object
// Parameters:
// size - The CGSize object that specifies the image size
- (id)initWithCGSize:(CGSize)size;

// Converts the MISize object to Core Graphics size
// The result must be released
- (CGSize)getCGSize;

@end

//----------------------------------------------------------------------------------------------------------------------

// Represents an image point in the two-dimensional space
@interface MIPoint : NSObject <NSCopying>

// Returns a copy of the MIPoint object
// Parameters:
// other - A poiter to the MIPoint object 
+ (id)pointWithMIPoint:(MIPoint*)other;

// Returns the MIPoint object initialized with the specified coordinates
// Parameters:
// x - the X-axis coordinate
// y - the Y-axis coordinate
+ (id)pointWithX:(float)x y:(float)y;

// Returns the MIPoint object initialized with the Core Graphics point
// Parameters:
// point - A poiter to the CGPoint object
+ (id)pointWithCGPoint:(CGPoint)point;

// The X-coordinate of a point in pixels
@property( nonatomic ) float x;
// The Y-coordinate of a point in pixels
@property( nonatomic ) float y;

// Returns a copy of the MIPoint object
// Parameters:
// other - A poiter to the MIPoint object 
- (id)initWithMIPoint:(MIPoint*)other;

// Returns the MIPoint object initialized with the specified coordinates
// Parameters:
// x - the X-axis coordinate
// y - the Y-axis coordinate
- (id)initWithX:(float)x y:(float)y;
// Returns the MIPoint object initialized with the Core Graphics point
// Parameters:
// point - A poiter to the CGPoint object
- (id)initWithCGPoint:(CGPoint)point;

// Converts the MIPoint object to the Core Graphics point
// The result must be released
- (CGPoint)getCGPoint;

@end

//----------------------------------------------------------------------------------------------------------------------

// Represents a rectangle on the image
@interface MIRect : NSObject <NSCopying>

// Returns a copy of the MIRect object
// Parameters:
// other - A poiter to the MIRect object 
+ (id)rectWithMIRect:(MIRect*)other;

// Creates the MIRect object given the coordinates of the top-left vertex and the size
// Parameters:
// origin - The MIPoint object with the coordinates of the top-left vertex 
// size - The MISize object with the rectangle size
+ (id)rectWithOrigin:(MIPoint*)origin size:(MISize*)size;

// Creates the MIRect object given the X- and Y-coordinates of the top-left vertex and the width and the height of the rectangle
// Parameters:
// x - The X-coordinate of the top-left vertex
// y - The Y-coordinate of the top-left vertex
// width - The width of the rectangle
// height - The height of the rectangle
+ (id)rectWithX:(float)x y:(float)y width:(float)width height:(float)height;

// Creates the MIRect object given the Core Graphics rectangle
// Parameters:
// rect - the Core Graphics rectangle
+ (id)rectWithCGRect:(CGRect)rect;

// The coordinates of the top-left vertex of the rectangle
@property( nonatomic, copy ) MIPoint* origin;
// The rectangle size
@property( nonatomic, copy ) MISize* size;

// Returns a copy of the MIRect object
// Parameters:
// other - A poiter to the MIRect object 
- (id)initWithMIRect:(MIRect*)other;

// Creates the MIRect object given the coordinates of the top-left vertex and the size
// Parameters:
// origin - The MIPoint object with the coordinates of the top-left vertex 
// size - The MISize object with the rectangle size
- (id)initWithOrigin:(MIPoint*)origin size:(MISize*)size;

// Creates the MIRect object given the X- and Y-coordinates of the top-left vertex and the width and the height of the rectangle
// Parameters:
// x - The X-coordinate of the top-left vertex
// y - The Y-coordinate of the top-left vertex
// width - The width of the rectangle
// height - The height of the rectangle
- (id)initWithX:(float)x y:(float)y width:(float)width height:(float)height;

// Creates the MIRect object given the Core Graphics rectangle
// Parameters:
// rect - the Core Graphics rectangle
- (id)initWithCGRect:(CGRect)rect;

// Converts the MIRect object to the Core Graphics rectangle
// The result must be released
- (CGRect)getCGRect;

@end

//----------------------------------------------------------------------------------------------------------------------

// Represents a quadrangle by the coordinates of its four vertexes
@interface MIQuad : NSObject <NSCopying>

// Returns a copy of the MIQuad object
// Parameters:
// other - A poiter to the MIQuad object 
+ (id)quadWithMIQuad:(MIQuad*)other;

// Creates the MIQuad object given vertexes
// Parameters:
// topLeft - A poiter to the top-left vertex
// topRight - A poiter to the top-right vertex
// bottomLeft - A poiter to the bottom-left vertex
// bottomRight - A poiter to the bottom-right vertex
+ (id)quadWithTopLeft:(MIPoint*)topLeft topRight:(MIPoint*)topRight
	bottomLeft:(MIPoint*)bottomLeft bottomRight:(MIPoint*)bottomRight;
	
// Creates the MIQuad object given the Core Graphics rectangle
// Parameters:
// rect - the Core Graphics rectangle
+ (id)quadWithCGRect:(CGRect)rect;

// The top-left vertex
@property( nonatomic, copy ) MIPoint* topLeft;
// The top-right vertex
@property( nonatomic, copy ) MIPoint* topRight;
// The bottom-left vertex
@property( nonatomic, copy ) MIPoint* bottomLeft;
// The bottom-right vertex
@property( nonatomic, copy ) MIPoint* bottomRight;

// Returns a copy of the MIQuad object
// Parameters:
// other - A poiter to the MIQuad object 
- (id)initWithMIQuad:(MIQuad*)other;

// Creates the MIQuad object given vertexes
// Parameters:
// topLeft - A poiter to the top-left vertex
// topRight - A poiter to the top-right vertex
// bottomLeft - A poiter to the bottom-left vertex
// bottomRight - A poiter to the bottom-right vertex
- (id)initWithTopLeft:(MIPoint*)topLeft topRight:(MIPoint*)topRight
	bottomLeft:(MIPoint*)bottomLeft bottomRight:(MIPoint*)bottomRight;

// Creates the MIQuad object given the Core Graphics rectangle
// Parameters:
// rect - the Core Graphics rectangle
- (id)initWithCGRect:(CGRect)rect;

@end
