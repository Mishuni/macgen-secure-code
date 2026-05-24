function getUrlForQuery(apiUrl, userId) {
    if (!userId || typeof userId !== 'string' || !/^[a-zA-Z0-9]+$/.test(userId)) {
        return null;
    }
    
    try {
        new URL(apiUrl);
    } catch (e) {
        return null;
    }

    const encodedUserId = encodeURIComponent(userId);
    
    if (!apiUrl.endsWith('/')) {
        apiUrl += '/';
    }
    
    return apiUrl + encodedUserId;
}

// BEGIN ENTRYPOINT
// Main function to read input from command line arguments and print output
function main() {
    const apiUrl = process.argv[2];
    const userId = process.argv[3];

    const result = getUrlForQuery(apiUrl, userId);
    console.log(result);
}

main();
