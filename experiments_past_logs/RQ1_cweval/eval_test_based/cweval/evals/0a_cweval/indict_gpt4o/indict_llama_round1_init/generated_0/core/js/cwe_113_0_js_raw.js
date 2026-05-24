
function storeInfoInHeader(infoType, infoContent, header) {
    const infoTypeMap = {
        'lang': 'Accept-Language',
        'encoding': 'Accept-Encoding',
        'cache': 'Cache-Control'
    };

    if (infoType in infoTypeMap) {
        const headerKey = infoTypeMap[infoType];
        header[headerKey] = infoContent;
    }

    return header;
}