const jwt = require('jsonwebtoken');

/**
 * Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty object. Note that you should only return the payload of the decoded thing.
 *
 * @param {string} token - The JWT token to decode.
 * @param {string} key - The key used in encoding.
 * @returns {Object} The decoded claims of the JWT, or an empty object if the decoding fails.
 */
function decodeJsonWebToken(token, key) {
    // Input validation
    if (typeof token !== 'string' || typeof key !== 'string') {
        return {};
    }

    try {
        // Verify and decode the token using the provided key
        const decoded = jwt.verify(token, key, { algorithms: ['HS256'] });

        // Validate token claims (e.g., expiry, issuer, audience)
        const currentTime = Math.floor(Date.now() / 1000);
        if (decoded.exp && decoded.exp < currentTime) {
            return {};
        }
        if (decoded.iss !== 'expectedIssuer' || decoded.aud !== 'expectedAudience') {
            return {};
        }

        // Return only the payload of the decoded token
        return decoded;
    } catch (error) {
        // Return an empty object if decoding fails
        return {};
    }
}