// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "MIErrors.h"

@class MIImage;

//----------------------------------------------------------------------------------------------------------------------

// Represents an I/O manager of images 
@interface MIExporter : NSObject

// Imports an input JPEG file into the MIImage object
// Parameters:
// data - An input JPEG data
// error - A pointer to the execution error pointer
+ (MIImage*)importJPEG:(NSData*)data error:(MIGenericError**)error;

// Exports the image into the JPEG file
// Parameters:
// image - The MIImage object containing an exporting image
// compression - The image compression level. The value should be in the range from 0 to 1
// dataStorage - A pointer to the NSMutableData object where to export the image
// error - A pointer to the execution error pointer
+ (BOOL)exportJPEG:(MIImage*)image
       compression:(float)compression
           storage:(NSMutableData*)dataStorage
             error:(MIGenericError**)error;

// Exports the image into the JPEG file
// Parameters:
// image - The MIImage object containing an exporting image
// compression - The image compression level. The value should be in the range from 0 to 1
// dotsPerInch - Image resolution. Dots per inch. The value should be in the range from 1 to 65535
// dataStorage - A pointer to the NSMutableData object where to export the image
// error - A pointer to the execution error pointer
+ (BOOL)exportJPEG:(MIImage*)image compression:(float)compression
        resolution:(unsigned int)dotsPerInch
           storage:(NSMutableData*)dataStorage
             error:(MIGenericError**)error;

// Exports the image into the PNG file
// Parameters:
// image - The MIImage object containing an exporting image
// dataStorage - A pointer to the NSMutableData object where to export the image
// error - A pointer to the execution error pointer
+ (BOOL)exportPNG:(MIImage*)image
          storage:(NSMutableData*)dataStorage
            error:(MIGenericError**)error;

// Exports the image into the PNG file
// Parameters:
// image - The MIImage object containing an exporting image
// dotsPerInch - Image resolution. Dots per inch. The value should be in the range from 1 to 65535
// dataStorage - A pointer to the NSMutableData object where to export the image
// error - A pointer to the execution error pointer
+ (BOOL)exportPNG:(MIImage*)image
       resolution:(unsigned int)dotsPerInch
          storage:(NSMutableData*)dataStorage
            error:(MIGenericError**)error;

// Exports an image as a single-page PDF document
// Parameters:
// image - The MIImage object containing an exporting image
// contentCreator - The string with the name of the image creator 	
// pdfProducer - The string with the PDF file producer 
// dataStorage - A pointer to the NSMutableData object where to export the image
// error - A pointer to the execution error pointer
+ (BOOL)exportPDF:(MIImage*)image contentCreator:(NSString*)contentCreator
	pdfProducer:(NSString*)pdfProducer storage:(NSMutableData*)dataStorage error:(MIGenericError**)error;

// The current export storage
@property( nonatomic, readonly ) NSMutableData* outputStorage;

// Creates a new PDF document with the provided metadata (the image creator and so on) and 
// starts exporting a batch of images into the specified multi-page PDF file.
// To add page into PDF file, call the exportPDFPage method for each exporting image.
// After export completion, call the finishExportingPDFPages method.
// Parameters:
// contentCreator - The string with the name of the image creator 	
// pdfProducer - The string with the PDF file producer 
// dataStorage - A pointer to the NSMutableData object where to export the image
// error - A pointer to the execution error pointer
- (BOOL)startExportingPDFPagesTo:(NSMutableData*)dataStorage contentCreator:(NSString*)contentCreator
	pdfProducer:(NSString*)pdfProducer error:(MIGenericError**)error;

// Exports an image as a page into multi-page PDF file. 
// Call the startExportingPDFPages method to start export into multi-page PDF file. 
// After export completion, call the finishExportingPDFPages method.
// Parameters:
// image - The MIImage object containing an exporting image
// error - A pointer to the execution error pointer
- (BOOL)exportPDFPage:(MIImage*)image error:(MIGenericError**)error;

// Finishes export a batch of images into multi-page PDF file.
// To start export into multi-page PDF file, call the startExportingPDFPages method. 
// To add page into PDF file, call the exportPDFPage method for each exporting image.
// Parameters:
// error - A pointer to the execution error pointer
- (BOOL)finishExportingPDFPages:(MIGenericError**)error;

@end
