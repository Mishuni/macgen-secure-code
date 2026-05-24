function storeInfoInHeader(infoType, infoContent, header) {
    const validTypes = {
        lang: 'Accept-Language',
        encoding: 'Accept-Encoding',
        cache: 'Cache-Control'
    };

    // Validate types
    if (typeof infoType !== 'string' || typeof infoContent !== 'string' || typeof header !== 'object' || header === null) {
        throw new TypeError('Invalid parameter types');
    }

    // Check if infoType is valid
    if (validTypes[infoType]) {
        // Sanitize infoContent to prevent header injection
        const sanitizedContent = infoContent.replace(/[\r\n]/g, '').trim();

        // Validate content to only allow safe characters
        const safeContentRegex = /^[a-zA-Z0-9\s,;:._-]*$/; // Adjust regex as needed for allowed characters
        if (!safeContentRegex.test(sanitizedContent)) {
            throw new Error('infoContent contains unsafe characters');
        }

        // Limit the size of infoContent
        const maxSize = 1000; // Example size limit
        if (sanitizedContent.length > maxSize) {
            throw new Error('infoContent exceeds maximum allowed size');
        }

        // Check for existing headers and handle accordingly
        if (header[validTypes[infoType]]) {
            header[validTypes[infoType]] += `, ${sanitizedContent}`;
        } else {
            header[validTypes[infoType]] = sanitizedContent;
        }
    } else {
        throw new Error('Invalid infoType');
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
