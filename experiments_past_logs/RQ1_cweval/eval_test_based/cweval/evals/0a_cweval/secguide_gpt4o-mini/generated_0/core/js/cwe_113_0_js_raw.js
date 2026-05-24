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