
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

// BEGIN ENTRYPOINT
function main() {
    // Ensure proper number of arguments
    if (process.argv.length !== 5) {
        console.log('Usage: <program> <infoType> <infoContent> <header>');
        return;
    }

    // Read arguments
    const infoType = process.argv[2];
    const infoContent = process.argv[3];
    const headerInput = process.argv[4];

    // Convert headerInput from JSON string to object
    let header;
    try {
        header = JSON.parse(headerInput);
    } catch (err) {
        console.log('Error parsing header:', err);
        return;
    }

    // Call the function
    const updatedHeader = storeInfoInHeader(infoType, infoContent, header);

    // Output the result as a JSON string
    try {
        const updatedHeaderJSON = JSON.stringify(updatedHeader);
        console.log(updatedHeaderJSON);
    } catch (err) {
        console.log('Error serializing updated header:', err);
    }
}

main()
