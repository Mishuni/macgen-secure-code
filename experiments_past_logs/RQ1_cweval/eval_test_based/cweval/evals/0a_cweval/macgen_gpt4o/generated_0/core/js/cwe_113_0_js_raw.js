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