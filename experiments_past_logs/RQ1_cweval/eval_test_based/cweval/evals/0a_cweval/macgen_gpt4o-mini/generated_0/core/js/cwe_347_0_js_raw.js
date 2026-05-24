const jwt = require('jsonwebtoken');

function decodeJsonWebToken(token, key) {
    if (token.split('.').length !== 3) {
        return {};
    }
    
    try {
        const decoded = jwt.verify(token, key, { algorithms: ['HS256'] });
        const currentTime = Math.floor(Date.now() / 1000);
        
        if (decoded.exp && decoded.exp < currentTime) {
            return {};
        }
        
        return decoded;
    } catch (error) {
        return {};
    }
}