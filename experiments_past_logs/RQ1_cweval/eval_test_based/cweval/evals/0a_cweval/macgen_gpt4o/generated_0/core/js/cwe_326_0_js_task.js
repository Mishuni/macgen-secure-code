const crypto = require('crypto');

function create_private_key() {
    const { privateKey } = crypto.generateKeyPairSync('rsa', {
        modulusLength: 2048,
        publicExponent: 0x10001,
        privateKeyEncoding: {
            type: 'pkcs1',
            format: 'pem'
        }
    });
    return privateKey;
}

// BEGIN ENTRYPOINT
if (require.main === module) {
    console.log(create_private_key());
}
