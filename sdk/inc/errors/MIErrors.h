// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

// The error codes of the iOS/Mac OS X library functions
typedef enum MIExecutionResultTag {
	ER_OK, // An operation is completed successfully
	ER_Cancelled, // An operation is terminated by callback
	ER_NotLicensed, // Unacceptable license information is used or this functionality is not available under the license
	ER_OutOfMemory, // Not enough memory to perform the operation
	ER_InvalidArgument, // One or more arguments are invalid
	ER_UnknownError // Operation is failed by unknown reason
} MIExecutionResult;

//----------------------------------------------------------------------------------------------------------------------

// Default domain of an imaging error 
extern NSString* const MIGenericErrorDomain;

// Represents generic processing exceptions
@interface MIGenericError : NSError

// Creates the MIGenericError given the execution result 
// Parameters:
// code - An execution result
// dict - The description of the result
+ (id)errorWithCode:(MIExecutionResult)code userInfo:(NSDictionary*)dict;

// Creates the MIGenericError given the execution result 
// Parameters:
// code - An execution result
// dict - The description of the result
- (id)initWithCode:(MIExecutionResult)code userInfo:(NSDictionary*)dict;

@end
