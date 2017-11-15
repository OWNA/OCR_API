// Copyright (C) ABBYY (BIT Software), 1993 - 2012. All rights reserved.

#import "MIOperationResultView.h"

@interface MIOperationResultView ()

// Cached drawing path
@property(nonatomic) CGMutablePathRef drawingPath;

// Perform initial view setup
- (void)configureSelf;

@end

@implementation MIOperationResultView

@synthesize imageSize;
@synthesize contents;
@synthesize contentOffset;
@synthesize zoomScale;
@synthesize drawingPath;

- (id)initWithFrame:(CGRect)frame
{
    self = [super initWithFrame:frame];
    if( self != nil ) {
        // setup the view and its contents
        [self configureSelf];
    }
    return self;
}

- (void)dealloc
{
    self.contents = nil;
    self.drawingPath = nil;
}

- (void)setContents:(id)_contents
{
    if(contents != _contents) {
        contents = _contents;
        self.drawingPath = [self createDrawingPath];
    }
}

- (void)drawRect:(CGRect)rect
{
    CGPathRef path = (CGPathRef)self.drawingPath;
    if( path != 0 ) {
        CGContextRef context = UIGraphicsGetCurrentContext();
        CGContextClipToRect( context, rect );
        CGContextTranslateCTM( context, -self.contentOffset.x, -self.contentOffset.y );
        CGContextScaleCTM( context, self.zoomScale, self.zoomScale );
        CGContextAddPath( context, path );
        CGContextSetLineWidth( context, 2.0 / self.zoomScale );
        CGContextSetStrokeColorWithColor( context, [UIColor redColor].CGColor );
        CGContextDrawPath( context, kCGPathStroke );

    }
}

- (void)configureSelf
{
    self.opaque = NO;
    self.userInteractionEnabled = NO;
    self.backgroundColor = [UIColor clearColor];
    self.clearsContextBeforeDrawing = NO; // custom drawing
    self.autoresizesSubviews = NO;
}

- (CGMutablePathRef)createDrawingPath
{
    return nil;
}



@end

//----------------------------------------------------------------------------------------------------------------------

@interface MIDetectedBlurView ()

// Additional paths for blurred & defocused blocks
@property( nonatomic, retain ) id drawingPath1;
@property( nonatomic, retain ) id drawingPath2;

- (void)addBlock:(MIRect*)block toPath:(CGMutablePathRef)path;

@end

@implementation MIDetectedBlurView

@synthesize drawingPath1;
@synthesize drawingPath2;

- (void)dealloc
{
    self.drawingPath1 = nil;
    self.drawingPath2 = nil;
}

- (void)drawRect:(CGRect)rect
{
    CGPathRef path = self.drawingPath;
    if( path != 0 ) {
        CGContextRef context = UIGraphicsGetCurrentContext();
        CGContextClipToRect( context, rect );
        CGContextTranslateCTM( context, -self.contentOffset.x, -self.contentOffset.y );
        CGContextScaleCTM( context, self.zoomScale, self.zoomScale );
        CGContextAddPath( context, path );
        CGContextSetLineWidth( context, 2.0 / self.zoomScale );
        CGContextSetStrokeColorWithColor( context, [UIColor redColor].CGColor );
        CGContextDrawPath( context, kCGPathStroke );
        // fill blurred blocks
        CGPathRef redPath = (CGPathRef)CFBridgingRetain(self.drawingPath1);
        if( redPath != 0 ) {
            CGContextAddPath( context, redPath );
            CGFloat colorComponents[] = { 1.0, 0, 0, 0.5 };
            CGContextSetFillColor( context, colorComponents );
            CGContextDrawPath( context, kCGPathFill );
        }
        // fill defocused blocks
        CGPathRef bluePath = (CGPathRef)CFBridgingRetain(self.drawingPath2);
        if( bluePath != 0 ) {
            CGContextAddPath( context, bluePath );
            CGFloat colorComponents[] = { 0, 0, 1.0, 0.5 };
            CGContextSetFillColor( context, colorComponents );
            CGContextDrawPath( context, kCGPathFill );
        }
    }
}

- (CGMutablePathRef)createDrawingPath
{
    CGMutablePathRef path = 0;
    if([self.contents isKindOfClass:[MIBlurInfo class]]) {
        MIBlurInfo* info = (MIBlurInfo*)self.contents;
        path = CGPathCreateMutable();
        const CGFloat blockSize = 256; // for now blocks are squares of known size
        const CGSize gridSize = CGSizeMake( ceilf( self.imageSize.width / blockSize ) * blockSize,
                                           ceilf( self.imageSize.height / blockSize ) * blockSize );
        CGFloat currentBlockX = 0;
        while ( currentBlockX <= gridSize.width ) {
            CGPathMoveToPoint( path, 0, currentBlockX, 0 );
            CGPathAddLineToPoint( path, 0, currentBlockX, gridSize.height );
            currentBlockX += blockSize;
        }
        CGFloat currentBlockY = 0;
        while ( currentBlockY <= gridSize.height ) {
            CGPathMoveToPoint( path, 0, 0, currentBlockY );
            CGPathAddLineToPoint( path, 0, gridSize.width, currentBlockY );
            currentBlockY += blockSize;
        }
        CGPathCloseSubpath( path );
        if( [info.blurredBlocks count] > 0 ) {
            // construct drawingPath1 here as a by-product
            CGMutablePathRef redPath = CGPathCreateMutable();
            for( MIRect* block in info.blurredBlocks ) {
                [self addBlock:block toPath:redPath];
            }
            CGPathCloseSubpath( redPath );
            self.drawingPath1 =(__bridge id) redPath;
        } else {
            self.drawingPath1 = nil;
        }
        if( [info.defocusedBlocks count] > 0 ) {
            // construct drawingPath2 here as a by-product
            CGMutablePathRef bluePath = CGPathCreateMutable();
            for( MIRect* block in info.defocusedBlocks ) {
                [self addBlock:block toPath:bluePath];
            }
            CGPathCloseSubpath( bluePath );
            self.drawingPath2 = (__bridge id)bluePath;
        } else {
            self.drawingPath2 = nil;
        }
    }
    return path;
}

- (void)addBlock:(MIRect*)block toPath:(CGMutablePathRef)path
{
    CGPathMoveToPoint( path, 0, block.origin.x, block.origin.y );
    CGPathAddLineToPoint( path, 0, block.origin.x + block.size.width, block.origin.y );
    CGPathAddLineToPoint( path, 0, block.origin.x + block.size.width, block.origin.y + block.size.height );
    CGPathAddLineToPoint( path, 0, block.origin.x, block.origin.y + block.size.height );
    CGPathCloseSubpath( path ); // bottomLeft -> topLeft
}

@end

//----------------------------------------------------------------------------------------------------------------------

@implementation MIDetectedGlareView

- (CGMutablePathRef)createDrawingPath
{
    CGMutablePathRef path = 0;
    if( [self.contents isKindOfClass:[MIGlareInfo class]] ) {
        MIGlareInfo* info = (MIGlareInfo*)self.contents;
        path = CGPathCreateMutable();
        // draw oval instead of ellipse to simplify
        CGFloat spotHalfwidth = sqrtf( info.mu02 / ( info.mu20 * info.mu02 - info.mu11 * info.mu11 ) );
        CGFloat spotHalfheight = sqrtf( info.mu20 / ( info.mu20 * info.mu02 - info.mu11 * info.mu11 ) );
        CGPathAddEllipseInRect( path, 0, CGRectMake( info.spotCenter.x - spotHalfwidth, info.spotCenter.y - spotHalfheight,
                                                    spotHalfwidth * 2, spotHalfheight * 2 ) );
        CGPathCloseSubpath(path);
    }
    return path;
}

@end
