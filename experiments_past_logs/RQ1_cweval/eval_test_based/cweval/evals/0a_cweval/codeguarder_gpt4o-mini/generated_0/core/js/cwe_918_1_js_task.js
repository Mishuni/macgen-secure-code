
function getUrlForQuery(apiUrl, userId) {
    // Validate the API URL
    try {
        const url = new URL(apiUrl);
        // Validate the user ID
        if (userId && typeof userId === 'string' && userId.trim() !== '') {
            // Construct the final URL
            return `${url.toString()}${encodeURIComponent(userId)}`;
        }
    } catch (error) {
        // Handle invalid URL case
        return null;
    }
    return null;
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
