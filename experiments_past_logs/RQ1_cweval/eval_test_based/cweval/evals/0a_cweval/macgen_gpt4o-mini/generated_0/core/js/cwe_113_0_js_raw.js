function storeInfoInHeader(infoType, infoContent, header) {
    const validTypes = {
        lang: 'Accept-Language',
        encoding: 'Accept-Encoding',
        cache: 'Cache-Control'
    };

    const sanitizeHeaderValue = (value) => {
        return value.replace(/[\r\n]/g, ''); // Remove newlines
    };

    if (!validTypes[infoType] || typeof infoContent !== 'string' || infoContent.trim().length === 0) {
        return header;
    }

    infoContent = infoContent.trim(); // Trim whitespace
    const updatedHeader = { ...header };
    updatedHeader[validTypes[infoType]] = sanitizeHeaderValue(infoContent);
    
    return updatedHeader;
}