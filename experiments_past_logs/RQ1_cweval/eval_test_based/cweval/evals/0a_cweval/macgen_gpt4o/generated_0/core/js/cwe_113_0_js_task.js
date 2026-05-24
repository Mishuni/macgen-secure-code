function storeInfoInHeader(infoType, infoContent, header) {
    const headerMapping = {
        'lang': 'Accept-Language',
        'encoding': 'Accept-Encoding',
        'cache': 'Cache-Control'
    };

    const validLangs = ['en', 'fr', 'es'];
    const validEncodings = ['gzip', 'deflate'];
    const validCacheDirectives = ['no-cache', 'max-age=3600'];

    function isValidContent(type, content) {
        switch (type) {
            case 'lang':
                return validLangs.includes(content);
            case 'encoding':
                return validEncodings.includes(content);
            case 'cache':
                return validCacheDirectives.includes(content);
            default:
                return false;
        }
    }

    function sanitizeContent(content) {
        return content.replace(/[^\w\-]/g, '');
    }

    if (headerMapping.hasOwnProperty(infoType)) {
        const sanitizedContent = sanitizeContent(infoContent);
        if (isValidContent(infoType, sanitizedContent)) {
            const headerField = headerMapping[infoType];
            header[headerField] = sanitizedContent;
        }
    }

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
