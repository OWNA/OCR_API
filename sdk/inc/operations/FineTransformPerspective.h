// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

@class MISize;
@class MIQuad;

//----------------------------------------------------------------------------------------------------------------------

// Performs transformation of the image by specified quadrangle. This interface extends the FineOperation interface
@interface FineTransformPerspective : FineOperation

// Creates the FineTransformPerspective object given input parameters
// Parameters:
// edges - vertices of the image quadrangle to transform
// size - The size for the resulting image. 
//	 If this parameter is null, the size of the bounding box is used
+ (id)fineTransformPerspectiveWithEdges:(MIQuad*)edges size:(MISize*)size;

// The MIQuad object that contains the image quadrangle to transform
@property( nonatomic, copy ) MIQuad* edges;
// The size for the resulting image 
@property( nonatomic, copy ) MISize* size;

// Initializes the object with given parameters
// Parameters:
// edges - vertices of the image quadrangle to transform
// size - The size for the resulting image. 
//	 If this parameter is null, the size of the bounding box is used
- (id)initWithEdges:(MIQuad*)edges size:(MISize*)size;

@end
