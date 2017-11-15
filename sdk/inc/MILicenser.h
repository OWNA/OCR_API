// Copyright (C) ABBYY (BIT Software), 1993 - 2011. All rights reserved.

#import "MIErrors.h"

@class MIGenericError;

//----------------------------------------------------------------------------------------------------------------------

// Describes the ABBYY Mobile Imaging SDK version
typedef struct MIVersionTag {
	NSInteger major;
	NSInteger minor;
	NSInteger modification;
	NSInteger build;
} MIVersion;

//----------------------------------------------------------------------------------------------------------------------

// Describes the ABBYY Mobile Imaging SDK license that allows you to use the library functionality
@interface MILicenser : NSObject

// Return the information about the current version
+ (MIVersion)versionInfo;

// Sets the license information 
// Parameters:
// licenseData - The data from the license file
// applicationId - A string with application identification.
// error - A pointer to the execution error pointer
// Important! The applicationId must correspond to the application ID in the license file.
+ (BOOL)setLicense:(NSData*)licenseData forApplication:(NSString*)applicationId error:(MIGenericError**)error;

// Returns the information about the active license
+ (NSString*)licenseInfo;

@end
