
function storeInfoInHeader(infoType, infoContent, header) {
    // Initialize a mapping of valid info types to their corresponding header keys
    const headerMap = {
        'lang': 'Accept-Language',
        'encoding': 'Accept-Encoding',
        'cache': 'Cache-Control'
    };

    // Check if the provided infoType is valid
    if (headerMap.hasOwnProperty(infoType)) {
        // Validate the infoContent to prevent unsafe data
        if (typeof infoContent === 'string' && infoContent.trim() !== '') {
            // Store the information in the header
            header[headerMap[infoType]] = infoContent;
        }
    }

    // Return the original header map if anything goes wrong
    return header;
}