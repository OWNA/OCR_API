// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

// A listener protocol that is used to deliver the results of the image processing. 
// This protocol is implemented on the client side.
@protocol MIListener <NSObject>

// Delivers the result to a listener object after the processing is finished.
// Parameters:
// result - The processing result
- (void)onProgressFinished:(id)result;

@end
