function storeInfoInHeader(infoType, infoContent, header) {
    // Define a mapping of valid information types to their corresponding header keys
    const infoTypeToHeaderKey = {
        'lang': 'Accept-Language',
        'encoding': 'Accept-Encoding',
        'cache': 'Cache-Control'
    };

    // Define specific validation patterns for each header type
    const validationPatterns = {
        'lang': /^[a-z]{2,3}(-[A-Z]{2,3})?$/, // e.g., en, en-US
        'encoding': /^(gzip|compress|deflate|br|identity|[\*])$/, // common encodings
        'cache': /^(no-cache|no-store|must-revalidate|max-age=\d+)$/ // common cache directives
    };

    // Check if the provided infoType is valid
    if (infoTypeToHeaderKey.hasOwnProperty(infoType)) {
        // Get the corresponding header key for the infoType
        const headerKey = infoTypeToHeaderKey[infoType];

        // Validate the infoContent based on the specific pattern for the infoType
        const validPattern = validationPatterns[infoType];
        if (typeof infoContent === 'string' && validPattern.test(infoContent)) {
            // Store the information content in the header under the specified key
            header[headerKey] = infoContent;
        } else {
            // Handle invalid infoContent
            throw new Error(`Invalid infoContent format for ${infoType}`);
        }
    } else {
        // Handle invalid infoType
        throw new Error('Invalid infoType');
    }

    // Return the updated header map
    return header;
}