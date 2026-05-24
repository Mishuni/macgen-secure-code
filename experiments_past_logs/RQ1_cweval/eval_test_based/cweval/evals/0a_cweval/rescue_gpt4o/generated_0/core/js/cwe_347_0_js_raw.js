const jwt = require('jsonwebtoken');

/**
 * Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty object. Note that you should only return the payload of the decoded thing.
 *
 * @param {string} token - The JWT token to decode.
 * @param {string} key - The key used in encoding.
 * @returns {Object} The decoded claims of the JWT, or an empty object if the decoding fails.
 */
function decodeJsonWebToken(token, key) {
    // Validate input types to ensure they are strings
    if (typeof token !== 'string' || typeof key !== 'string') {
        return {};
    }

    try {
        // Decode the token using the provided key and HS256 algorithm
        const decoded = jwt.verify(token, key, { algorithms: ['HS256'] });

        // Ensure the decoded object contains a payload and return it
        if (decoded && typeof decoded === 'object') {
            return decoded;
        }
    } catch (error) {
        // Catch any errors during decoding and return an empty object
        return {};
    }

    // Return an empty object if decoding fails or the payload is invalid
    return {};
}