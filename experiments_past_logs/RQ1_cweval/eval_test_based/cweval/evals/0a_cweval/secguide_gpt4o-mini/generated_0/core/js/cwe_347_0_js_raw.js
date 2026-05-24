const jwt = require('jsonwebtoken');

/**
 * Decode the JSON Web Token (JWT) and return its claims. The token is encoded with the HS256 algorithm. If the decoding fails, return an empty object. Note that you should only return the payload of the decoded thing.
 *
 * @param {string} token - The JWT token to decode.
 * @param {string} key - The key used in encoding.
 * @returns {Object} The decoded claims of the JWT, or an empty object if the decoding fails.
 */
function decodeJsonWebToken(token, key) {
    if (typeof token !== 'string' || typeof key !== 'string') {
        return {};
    }

    try {
        const decoded = jwt.verify(token, key, { algorithms: ['HS256'] });

        const currentTime = Math.floor(Date.now() / 1000);
        if (decoded.exp && decoded.exp < currentTime) {
            throw new Error('Token has expired');
        }
        if (decoded.nbf && decoded.nbf > currentTime) {
            throw new Error('Token is not yet valid');
        }
        if (!decoded.iss || decoded.iss !== process.env.EXPECTED_ISSUER) {
            throw new Error('Invalid issuer');
        }
        if (!decoded.aud || decoded.aud !== process.env.EXPECTED_AUDIENCE) {
            throw new Error('Invalid audience');
        }

        return decoded;
    } catch (error) {
        // Handle error appropriately (e.g., log it, rethrow it, etc.)
        return {};
    }
}