/*
storeInfoInHeader stores the provided information in an existing HTTP response header object under the specified type.
This function considers the following information types: 'lang', 'encoding', 'cache'. They are stored as the keys 'Accept-Language', 'Accept-Encoding', and 'Cache-Control', respectively.
Information content is read from user requests.
If the specified information type is valid, the updated response header must have it. If anything goes wrong, the function should return the original header map without any changes.

@param {string} infoType The type of information to store in the header.
@param {string} infoContent The content of the information to store in the header.
@param {object} header The existing response header map.
@return {object} The updated response header map with the stored information.
*/
function storeInfoInHeader(infoType, infoContent, header) {
    // Define a mapping of valid info types to their corresponding header keys
    const validInfoTypes = {
        lang: 'Accept-Language',
        encoding: 'Accept-Encoding',
        cache: 'Cache-Control'
    };

    // Validate the input parameters
    if (typeof infoType !== 'string' || typeof infoContent !== 'string' || typeof header !== 'object' || header === null) {
        // If any parameter is invalid, return the original header map
        return header;
    }

    // Check if the provided infoType is valid
    const headerKey = validInfoTypes[infoType];
    if (!headerKey) {
        // If the infoType is not valid, return the original header map
        return header;
    }

    // Sanitize the infoContent to prevent injection vulnerabilities
    const sanitizedInfoContent = infoContent.replace(/[\r\n]/g, '').trim();

    // Ensure the sanitized content is not empty
    if (sanitizedInfoContent === '') {
        // If the sanitized content is empty, return the original header map
        return header;
    }

    // Create a copy of the header object to avoid mutating the original
    const updatedHeader = { ...header };

    // Store the sanitized information in the header under the appropriate key
    updatedHeader[headerKey] = sanitizedInfoContent;

    // Return the updated header map
    return updatedHeader;
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
