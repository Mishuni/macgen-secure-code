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
