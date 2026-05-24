
function storeInfoInHeader(infoType, infoContent, header) {
    // Validate the infoType to ensure it is one of the expected types
    const validInfoTypes = {
        'lang': 'Accept-Language',
        'encoding': 'Accept-Encoding',
        'cache': 'Cache-Control'
    };

    // Check if the provided infoType is valid
    if (!validInfoTypes.hasOwnProperty(infoType)) {
        return header; // Return the original header if the infoType is invalid
    }

    // Validate the infoContent to ensure it does not contain any control characters
    if (typeof infoContent !== 'string' || /[\x00-\x1F\x7F]/.test(infoContent)) {
        throw new Error("Invalid infoContent: contains control characters");
    }

    // Store the information in the header under the appropriate key
    const headerKey = validInfoTypes[infoType];
    header[headerKey] = infoContent;

    return header; // Return the updated header
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
