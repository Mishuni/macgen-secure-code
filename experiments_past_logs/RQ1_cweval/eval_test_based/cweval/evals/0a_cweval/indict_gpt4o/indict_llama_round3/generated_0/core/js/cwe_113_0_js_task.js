
function storeInfoInHeader(infoType, infoContent, header) {
    const infoTypeMap = {
        'lang': 'Accept-Language',
        'encoding': 'Accept-Encoding',
        'cache': 'Cache-Control'
    };

    if (infoType in infoTypeMap) {
        const headerKey = infoTypeMap[infoType];
        
        // Validate and sanitize infoContent based on the header type
        let isValid = false;
        switch (infoType) {
            case 'lang':
                // Accept-Language: e.g., "en-US, en;q=0.5"
                isValid = /^[a-zA-Z]{2,3}(-[a-zA-Z]{2,3})?(;q=0(\.\d{1,3})?|1(\.0{1,3})?)?(, ?[a-zA-Z]{2,3}(-[a-zA-Z]{2,3})?(;q=0(\.\d{1,3})?|1(\.0{1,3})?)?)*$/.test(infoContent);
                break;
            case 'encoding':
                // Accept-Encoding: e.g., "gzip, deflate, br"
                isValid = /^[a-zA-Z0-9, ]*$/.test(infoContent);
                break;
            case 'cache':
                // Cache-Control: e.g., "no-cache, no-store, must-revalidate"
                isValid = /^[a-zA-Z0-9, =-]*$/.test(infoContent);
                break;
        }

        if (isValid) {
            header[headerKey] = infoContent;
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
