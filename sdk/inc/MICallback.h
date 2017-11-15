// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

// This is a callback interface that is used to deliver information about the approximate percentage of the image processing to the client. 
// The interface is implemented on the client side. 
@protocol MICallback <NSObject>

// Delivers information about the approximate percentage of the image processing to the client.
// It returns non-zero value to break the image processing
// Parameters:
// progress - The percentage of the current work which has already been done. It is in the range from 0 to 100. 
- (int)onProgressUpdated:(int)progress;

@end
