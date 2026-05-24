
function storeInfoInHeader(infoType, infoContent, header) {
    // Define a mapping of infoType to header keys
    const headerMap = {
        'lang': 'Accept-Language',
        'encoding': 'Accept-Encoding',
        'cache': 'Cache-Control'
    };

    // Check if the provided infoType is valid
    if (headerMap.hasOwnProperty(infoType)) {
        // Store the infoContent in the appropriate header key
        header[headerMap[infoType]] = infoContent;
        return header; // Return the updated header
    }

    // If the infoType is invalid, return the original header unchanged
    return header;
}