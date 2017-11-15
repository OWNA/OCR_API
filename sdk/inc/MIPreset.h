// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "FineOperation.h"

// Contains a number of functions that have preset processing options for some common types of images 
// such as black-and-white documents, business card, and so on.
@interface MIPreset : FineOperation

// Creates the processing options for black-and-white documents.
+ (id)blackAndWhiteDocumentPreset;

// Creates the processing options for blurry, out-of-focus, dark pictures
+ (id)spyShotPreset;

// Creates the processing options for business cards.
+ (id)businessCardPreset;

// Creates the processing options for receipts.
+ (id)receiptPreset;

// Creates the processing options for color documents.
+ (id)colorDocumentPreset;

// Creates the processing options for light-on-dark documents.
+ (id)lightOnDarkDocumentPreset;

// Creates the processing options for stamped papers.
+ (id)stampedPaperPreset;

// Creates the processing options for street view pictures with high level of noise. 
+ (id)streetShotPreset;

// Initialize no-op preset
- (id)init;

@end
