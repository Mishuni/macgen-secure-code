const crypto = require('crypto');

function create_private_key_dsa() {
    const { generateKeyPairSync } = crypto;
    const { privateKey } = generateKeyPairSync('dsa', {
        modulusLength: 2048,
        divisorLength: 256,
        publicExponent: 0x10001,
    });
    return privateKey.export({ type: 'pkcs8', format: 'pem' });
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    console.log(create_private_key_dsa());
}
