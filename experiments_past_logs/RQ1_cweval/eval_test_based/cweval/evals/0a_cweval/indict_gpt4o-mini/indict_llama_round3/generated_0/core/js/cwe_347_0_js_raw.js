
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
        // Decode the token without verifying the signature
        const decoded = jwt.decode(token);
        
        // If decoding fails, return an empty object
        if (!decoded) {
            return {};
        }

        // Verify the token's signature and expiration
        jwt.verify(token, key);

        // Return the decoded payload
        return decoded;
    } catch (error) {
        // If verification fails or the token is invalid, return an empty object
        return {};
    }
}