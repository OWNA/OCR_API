// Copyright (C) ABBYY (BIT Software), 1993 - 2012. All rights reserved.

// Basic view that acts like an overlay and visualizes operation result
@interface MIOperationResultView : UIView

// Source image info
@property( nonatomic ) CGSize imageSize;
// Result contents
@property( nonatomic, retain ) id contents;
// Zooming support
@property( nonatomic ) CGPoint contentOffset;
@property( nonatomic ) CGFloat zoomScale;

// Create drawing path; to be overridden in subclasses
- (CGMutablePathRef)createDrawingPath;

@end

//----------------------------------------------------------------------------------------------------------------------

@interface MIDetectedBlurView : MIOperationResultView
@end

//----------------------------------------------------------------------------------------------------------------------

@interface MIDetectedGlareView : MIOperationResultView
@end
