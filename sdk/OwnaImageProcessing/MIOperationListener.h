// Copyright (C) ABBYY (BIT Software), 1993 - 2012. All rights reserved.

// Single file contains all results, new ones are appended to the end of the file
extern NSString* const ListenerLogFileName;

// Image processing operation index
typedef enum MIFineOperation {
    FO_Undefined = -1,
    FO_DetectBlur,
    FO_DetectGlare,
    FO_DetectNoise,
    FO_RecognizeEdges,
    FO_ReceiptPreset,
    FO_Total // number of operations
} MIFineOperation;

//----------------------------------------------------------------------------------------------------------------------

// Listener provides basic logging support for image operation results
@interface MIOperationListener : NSObject <MIListener>

// Source image metadata
@property UIImageOrientation imageOrientation;
@property CGSize imageSize;
// Cached operation result
@property( copy ) id operationResult;

// Adjust the resulting data using source image metadata; to be overridden in subclasses
- (id)adjustResult:(id)result;

// File handle ready to append a new data
- (NSFileHandle*)logFile;
// Timestamp
- (NSString*)timestampWithTime:(NSDate*)date;
// Name of the operation; to be overridden in subclasses
- (NSString*)operationName;
// Operation's result in readable form; to be overridden in subclasses
- (NSString*)readableResult;
- (NSMutableDictionary*)dictionaryResult;

// Pack the resulting data to readable log string
- (NSString*)operationLogWithTime:(NSDate*)date;

@end

//----------------------------------------------------------------------------------------------------------------------

@interface MIDetectBlurListener : MIOperationListener
@end

//----------------------------------------------------------------------------------------------------------------------

@interface MIDetectGlareListener : MIOperationListener
@end

//----------------------------------------------------------------------------------------------------------------------

@interface MIDetectNoiseListener : MIOperationListener
@end
