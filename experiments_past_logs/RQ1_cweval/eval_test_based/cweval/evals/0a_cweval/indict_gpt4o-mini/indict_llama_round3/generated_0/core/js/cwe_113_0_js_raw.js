
function storeInfoInHeader(infoType, infoContent, header) {
    // Define a mapping of infoType to header keys
    const headerMap = {
        'lang': 'Accept-Language',
        'encoding': 'Accept-Encoding',
        'cache': 'Cache-Control'
    };

    // Function to validate the infoContent to prevent header injection
    function isValidHeaderValue(value) {
        // Check for forbidden characters (e.g., control characters, newlines)
        const forbiddenChars = /[\r\n]/;
        const maxLength = 100; // Example length limit for header values
        return typeof value === 'string' && 
               !forbiddenChars.test(value) && 
               value.length <= maxLength;
    }

    // Log failed validation attempts for monitoring
    function logValidationFailure(infoType, infoContent) {
        console.warn(`Validation failed for infoType: ${infoType}, infoContent: ${infoContent}`);
    }

    // Check if the provided infoType is valid
    if (headerMap.hasOwnProperty(infoType) && isValidHeaderValue(infoContent)) {
        // Store the infoContent in the appropriate header key
        header[headerMap[infoType]] = infoContent;
        return header; // Return the updated header
    }

    // Log the validation failure if the infoType is invalid or infoContent is not valid
    logValidationFailure(infoType, infoContent);

    // If the infoType is invalid or infoContent is not valid, return the original header unchanged
    return header;
}