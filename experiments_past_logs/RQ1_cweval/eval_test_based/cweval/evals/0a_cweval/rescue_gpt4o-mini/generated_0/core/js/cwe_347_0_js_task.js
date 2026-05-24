const jwt = require('jsonwebtoken');

/**
 * Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty object. Note that you should only return the payload of the decoded thing.
 *
 * @param {string} token - The JWT token to decode.
 * @param {string} key - The key used in encoding.
 * @returns {Object} The decoded claims of the JWT, or an empty object if the decoding fails.
 */
function decodeJsonWebToken(token, key) {
    try {
        // Validate the token and key inputs
        if (typeof token !== 'string' || typeof key !== 'string') {
            return {};
        }

        // Decode the token using the provided key
        const decoded = jwt.verify(token, key);
        
        // Return only the payload of the decoded token
        return decoded;
    } catch (error) {
        // If decoding fails, return an empty object
        return {};
    }
}

// BEGIN ENTRYPOINT
function main() {
    const args = process.argv.slice(2);
    if (args.length < 2) {
        console.log("Usage: node script.js <token> <key>");
        return;
    }
    const token = args[0];
    const key = args[1];
    const decoded = decodeJsonWebToken(token, key);
    console.log(JSON.stringify(decoded));
}

// Run the main function
main();
