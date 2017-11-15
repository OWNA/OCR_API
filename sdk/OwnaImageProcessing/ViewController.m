//
//  ViewController.m
//  OwnaImageProcessing
//
//  Created by Michel on 10/14/16.
//  Copyright © 2016 Acodef. All rights reserved.
//

#import "ViewController.h"
#import "MIOperationListener.h"
#import "MIOperationResultView.h"

@import Photos;

@interface ViewController ()
@property( nonatomic, retain ) NSOperationQueue* operationQueue;
@property( nonatomic, retain ) FineOperation* currentOperation;
@property( nonatomic, retain ) PHImageRequestOptions* requestOptions;
@property( nonatomic, retain ) MIOperationResultView* operationOverlay;
@property (weak, nonatomic) IBOutlet UIButton *ProcessButton;
@property (weak, nonatomic) IBOutlet UIImageView *ImageView;
@property (weak, nonatomic) IBOutlet UIProgressView *ProgressView;
@property (weak, nonatomic) IBOutlet UIScrollView *scrollView;

@end

@implementation ViewController
{
    NSMutableArray *imageNames;
    NSMutableArray *imageAssets;
    NSMutableDictionary *imagesResults;
    int currentImageIndex;
    int currentOperationIndex;
}
@synthesize operationQueue;
@synthesize scrollView;


- (id)init
{
    self = [super init];
    if( self != nil ) {
        self.operationQueue = [[NSOperationQueue alloc] init];

        self.requestOptions = [[PHImageRequestOptions alloc] init];
        self.requestOptions.resizeMode   = PHImageRequestOptionsResizeModeExact;
        self.requestOptions.deliveryMode = PHImageRequestOptionsDeliveryModeHighQualityFormat;
        self.requestOptions.synchronous = true;
    }
    return self;
}

- (void)onProcessingUpdated:(MIAsyncProcessor*)processor index:(int)index progress:(int)progress
{
    // update processing progress
    self.ProgressView.progress = progress / 100.0;
}

- (void)onProcessingFinished:(MIAsyncProcessor*)processor code:(MIExecutionResult)code
{
    self.ProgressView.progress = 0;
    MIOperationListener* currentListener = ((FineResultOperation*)self.currentOperation).listener;
    UIAlertController * view= [UIAlertController
                               alertControllerWithTitle:@"Result"
                               message:[currentListener readableResult]
                               preferredStyle:UIAlertControllerStyleAlert];
    UIAlertAction* cancel = [UIAlertAction
                             actionWithTitle:@"Ok"
                             style:UIAlertActionStyleDefault
                             handler:^(UIAlertAction * action) {
                                 [view dismissViewControllerAnimated:YES completion:nil];
                             }];
    [view addAction:cancel];
    //[self presentViewController:view animated:YES completion:nil];
    MIOperationResultView* resultView = self.operationOverlay;
    if( false && resultView != nil ) {
        resultView.imageSize = currentListener.imageSize;
        resultView.contents = currentListener.operationResult;
        resultView.contentOffset = self.scrollView.contentOffset;
        resultView.zoomScale = self.scrollView.zoomScale;
        [self.view insertSubview:resultView aboveSubview:self.scrollView];
        [resultView setNeedsDisplay];
    }
    NSString* imageName = imageNames[currentImageIndex];
    NSLog(@"%@", imageName);
    if (imagesResults[imageName] == nil) {
        imagesResults[imageName] = [[NSMutableDictionary alloc] init];
    }
    //[self printResult];
    imagesResults[imageName][[currentListener operationName]] = [currentListener dictionaryResult];
    [self incrementProcessIndex];
    [self processNextAsset];
}

- (IBAction)galleryButtonPressed:(id)sender {
    UIImagePickerController* imagePickerController = [[UIImagePickerController alloc] init];
    imagePickerController.delegate = self;
    [self presentModalViewController:imagePickerController animated:YES];
}

- (void)imagePickerController:(UIImagePickerController*)picker didFinishPickingMediaWithInfo:(NSDictionary*)info
{
    [self dismissViewControllerAnimated];
    UIImage* originalImage = [info objectForKey:UIImagePickerControllerOriginalImage];
    [self resetProcessIndex];
    [self handleImage:originalImage];
}

- (void)dismissViewControllerAnimated
{
    [self dismissViewControllerAnimated:YES completion:0];
}

- (void) incrementProcessIndex
{
    if (currentOperationIndex < 2) {
        currentOperationIndex += 1;
    } else if (currentImageIndex < imageAssets.count) {
        currentOperationIndex = 0;
        currentImageIndex += 1;
    }
}

- (void) resetProcessIndex
{
    currentOperationIndex = 0;
    currentImageIndex = 0;
}


- (void) processAlbum:(PHAssetCollection*)collection
{
    // Find the album
    PHFetchOptions *fetchOptions = [[PHFetchOptions alloc] init];
    fetchOptions.predicate = [NSPredicate predicateWithFormat:@"title = %@", collection.localizedTitle];
    PHFetchResult *assets = [PHAsset fetchAssetsInAssetCollection:collection options:nil];
    imageNames = [NSMutableArray arrayWithCapacity:[assets count]];
    imagesResults = [NSMutableDictionary new];
    imageAssets = [NSMutableArray new];

    [assets enumerateObjectsUsingBlock:^(PHAsset *asset, NSUInteger idx, BOOL *stop) {
        [imageAssets addObject:asset];
        if (imageAssets.count == assets.count) {
            [self resetProcessIndex];
            [self processNextAsset];
        }
    }];
}

- (void)setupImage:(UIImage*)image
{
    // adjust content frame and set the content
    self.scrollView.zoomScale = 1.0;
    self.ImageView.frame = CGRectMake( 0, 0, image.size.width, image.size.height );
    self.ImageView.image = image;
    // showing entire image by default
    CGFloat defaultZoomScale = 1.0;
    if( image != nil ) {
        CGSize viewSize = self.scrollView.frame.size;
        defaultZoomScale = MIN( viewSize.height / image.size.height, viewSize.width / image.size.width );
    }
    self.scrollView.contentOffset = CGPointZero;
    self.scrollView.contentSize = image.size;
    self.scrollView.minimumZoomScale = defaultZoomScale;
    self.scrollView.zoomScale = defaultZoomScale;
}

- (UIView*)viewForZoomingInScrollView:(UIScrollView*)_scrollView
{
    return self.ImageView;
}

- (void)scrollViewDidScroll:(UIScrollView*)_scrollView
{
    self.operationOverlay.contentOffset = _scrollView.contentOffset;
    [self.operationOverlay setNeedsDisplay];
}

- (void)scrollViewDidZoom:(UIScrollView*)_scrollView
{
    // centering content view
    CGSize margins = CGSizeMake( _scrollView.frame.size.width >= _scrollView.contentSize.width
                                ? _scrollView.frame.size.width - _scrollView.contentSize.width
                                : 0, _scrollView.frame.size.height >= _scrollView.contentSize.height
                                ? _scrollView.frame.size.height - _scrollView.contentSize.height
                                : 0 );
    _scrollView.contentInset = UIEdgeInsetsMake( margins.height / 2.0, margins.width / 2.0, 0, 0 );
    
    self.operationOverlay.contentOffset = _scrollView.contentOffset;
    self.operationOverlay.zoomScale = _scrollView.zoomScale;
    [self.operationOverlay setNeedsDisplay];
}

- (void) printResult
{
    NSError *error;
    NSData *jsonData = [NSJSONSerialization
                        dataWithJSONObject:imagesResults
                        options:NSJSONWritingPrettyPrinted
                        error:&error];
    if (! jsonData) {
        NSLog(@"Got an error: %@", error);
    } else {
        NSString *jsonString = [[NSString alloc] initWithData:jsonData encoding:NSUTF8StringEncoding];
        printf("%s", [jsonString UTF8String]);
    }

}

- (void) processNextAsset
{
    if (currentImageIndex >= imageAssets.count) {
        NSLog(@"We are done - no more images left from %lu images", (unsigned long)imageAssets.count);
        [self printResult];
        return;
    }
    PHImageManager *manager = [PHImageManager defaultManager];
    [manager requestImageForAsset:imageAssets[currentImageIndex]
                       targetSize:PHImageManagerMaximumSize
                      contentMode:PHImageContentModeDefault
                          options:self.requestOptions
                    resultHandler:^void(UIImage *image, NSDictionary *info) {
                        NSURL *path = [info objectForKey:@"PHImageFileURLKey"];
                        if (currentOperationIndex == 0) {
                            [imageNames addObject:[path lastPathComponent]];
                        }
                        [self handleImage:image];
                    }];
}

- (void) handleImage:(UIImage *)image
{
    [self setupImage:image];
    MIImage* source = [MIImage imageWithCGImage:image.CGImage];
    FineOperation* operation = nil;
    MIOperationListener* listener = nil;
    MIOperationResultView* overlay = nil;
    
    switch (currentOperationIndex) {
        case 1:
            overlay =  [[MIDetectedGlareView alloc] initWithFrame:self.scrollView.frame];
            listener = [[MIDetectGlareListener alloc] init];
            operation = [FineDetectGlare fineDetectGlareWithListener:listener greyscale:NO mode:FALSE];
            break;
        case 0:
            overlay =  [[MIDetectedBlurView alloc] initWithFrame:self.scrollView.frame];
            listener = [[MIDetectBlurListener alloc] init];
            operation = [FineDetectBlur fineDetectBlurWithListener:listener greyscale:NO mode:FALSE];
            break;
        case 2:
            listener = [[MIDetectNoiseListener alloc] init];
            operation = [FineDetectNoise fineDetectNoiseWithListener:listener greyscale:NO mode:FALSE];
            break;
        default:
            break;
    }
    listener.imageOrientation = self.ImageView.image.imageOrientation;
    listener.imageSize = self.ImageView.image.size;
    
    if (self.operationOverlay) {
        [self.operationOverlay removeFromSuperview];
    }
    self.operationOverlay = overlay;
    self.currentOperation = operation;
    MIAsyncProcessor* processor = [MIAsyncProcessor asyncProcessorWithImage:[source copy] delegate:self];
    self.operationQueue = [[NSOperationQueue alloc] init];
    [processor execute:[NSArray arrayWithObject:operation] inQueue:operationQueue];

}

- (IBAction)processButtonPressed:(id)sender {
    PHFetchOptions *userAlbumsOptions = [PHFetchOptions new];
    userAlbumsOptions.predicate = [NSPredicate predicateWithFormat:@"estimatedAssetCount > 0"];
    
    PHFetchResult *userAlbums = [PHAssetCollection fetchAssetCollectionsWithType:PHAssetCollectionTypeAlbum subtype:PHAssetCollectionSubtypeAny options:userAlbumsOptions];
    
    UIAlertController * view= [UIAlertController
                               alertControllerWithTitle:@"Select your Album"
                               message:@"Chose which album to parse photos from"
                               preferredStyle:UIAlertControllerStyleActionSheet];
    UIAlertAction* cancel = [UIAlertAction
                        actionWithTitle:@"Cancel"
                         style:UIAlertActionStyleDefault
                         handler:^(UIAlertAction * action) {
                             [view dismissViewControllerAnimated:YES completion:nil];
                         }];
    [userAlbums enumerateObjectsUsingBlock:^(PHAssetCollection *collection, NSUInteger idx, BOOL *stop) {
        UIAlertAction* ok = [UIAlertAction
                             actionWithTitle:collection.localizedTitle
                             style:UIAlertActionStyleDefault
                             handler:^(UIAlertAction * action) {
                                 [view dismissViewControllerAnimated:YES completion:nil];
                                 [self processAlbum:collection];
                             }];
        [view addAction:ok];
    }];
    [view addAction:cancel];
    [self presentViewController:view animated:YES completion:nil];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    // Do any additional setup after loading the view, typically from a nib.
    self.ProgressView.progress = 0.0;
}


- (void)didReceiveMemoryWarning {
    [super didReceiveMemoryWarning];
    // Dispose of any resources that can be recreated.
}


@end
