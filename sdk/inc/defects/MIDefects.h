// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

@class MIPoint;

//----------------------------------------------------------------------------------------------------------------------

// Represents the detection results of the noise level as the signal to noise ratio
@interface MINoiseInfo : NSObject <NSCopying>

// The ratio of the signal to noise
@property( nonatomic ) float signalToNoiseRatio;
// Specifies whether the high noise level is detected 
@property( nonatomic, getter = isHigh ) BOOL high;

@end

//----------------------------------------------------------------------------------------------------------------------

// Represents a glare spot on the image. The program creates an equation describing the glare spot as an ellipse, 
// so the mu02, mu11, and mu20 properties correspond to the equation coefficients and the ellipse focus.
@interface MIGlareInfo : NSObject <NSCopying>

// A coefficient of the ellipse equation
@property( nonatomic ) float mu02;
// A coefficient of the ellipse equation
@property( nonatomic ) float mu11;
// A coefficient of the ellipse equation
@property( nonatomic ) float mu20;
// The center of the glare spot
@property( nonatomic, copy ) MIPoint* spotCenter;
// The optimal threshold of glare binarization
@property( nonatomic ) int optimalBinarizationThreshold;
// Specifies whether glare is detected 
@property( nonatomic, getter = isDetected ) BOOL detected;

@end

//----------------------------------------------------------------------------------------------------------------------

// Represents blurred and defocused image blocks. Before looking for defects, the entire image is divided into blocks, 
// and each block is analyzed to determine whether it has any text or not. 
// All properties of this class are computed relative to the area of the image made up of blocks containing the text.
@interface MIBlurInfo : NSObject <NSCopying>

// The size of the area with defects, where the program cannot define the type of the defect, 
// relatively to the size of the areas with text
@property( nonatomic ) float undefinedSize;
// The size of the areas with text relatively to the size of the image
@property( nonatomic ) float examinedSize;
// The size of the motion blurred area relatively to the size of the areas with text
@property( nonatomic ) float motionBlurSize;
// The size of the defocused area relatively to the size of the areas with text
@property( nonatomic ) float defocusSize;
// An array of the blurred blocks
@property( nonatomic, copy ) NSArray* blurredBlocks;
// An array of the defocused blocks
@property( nonatomic, copy ) NSArray* defocusedBlocks;
// Specifies whether heavy blur is detected
@property( nonatomic, getter = isDetected ) BOOL detected;

@end

//----------------------------------------------------------------------------------------------------------------------

// Container for all known defects
@interface MIAllDefectsInfo : NSObject <NSCopying>

@property( nonatomic, copy ) MINoiseInfo* noiseInfo;

@property( nonatomic, copy ) MIBlurInfo* blurInfo;

@property( nonatomic, copy ) MIGlareInfo* glareInfo;

@end