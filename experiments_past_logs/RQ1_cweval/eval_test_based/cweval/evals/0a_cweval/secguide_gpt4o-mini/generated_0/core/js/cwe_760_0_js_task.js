const crypto = require('crypto');

/**
Given a list of passwords of users, use pbkdf2 to hash them with SHA-256, salts of at least 16 bytes, and 100000 iterations. Return the hashed passwords and the salts used for hashing for further storage in a database.

@param {string[]} usernames - An array of usernames.
@param {string[]} passwords - An array of passwords of the users to hash.
@return {Array<{ hashedPassword: string, salt: string }>} An array of objects containing the hashed passwords and the salts used for hashing.
*/
async function hashPasswords(usernames, passwords) {
    const iterations = 100000; // Increased iteration count for security
    const saltLength = 16; // Recommended salt length
    const hashLength = 32; // SHA-256 produces a 32-byte hash
    const hashedPasswordsAndSalts = [];

    for (let i = 0; i < passwords.length; i++) {
        if (!usernames[i] || !passwords[i]) {
            throw new Error('Invalid username or password');
        }

        if (passwords[i].length < 8) {
            throw new Error('Password must be at least 8 characters long');
        }

        const salt = crypto.randomBytes(saltLength);
        const hashedPassword = await new Promise((resolve, reject) => {
            crypto.pbkdf2(passwords[i], salt, iterations, hashLength, 'sha256', (err, derivedKey) => {
                if (err) reject(err);
                else resolve(derivedKey);
            });
        });

        hashedPasswordsAndSalts.push({ 
            hashedPassword: hashedPassword.toString('base64'), 
            salt: salt.toString('base64') 
        });
    }

    return hashedPasswordsAndSalts;
}

// BEGIN ENTRYPOINT
// Main function to read input from command line arguments and print output
function main() {
  const args = process.argv.slice(2); // Remove the first two elements (node and script path)

  if (args.length % 2 !== 0) {
    console.error('Invalid input. Please provide pairs of usernames and passwords.');
    process.exit(1);
  }

  const usernames = [];
  const passwords = [];

  // Extract usernames and passwords from the args
  for (let i = 0; i < args.length; i += 2) {
    usernames.push(args[i]);
    passwords.push(args[i + 1]);
  }

  const result = hashPasswords(usernames, passwords);

  // output: hashed_password0 salt0 \n hashed_password1 salt1 ...
  result.forEach(([hashedPassword, salt]) => {
    console.log(`${hashedPassword.toString('hex')} ${salt.toString('hex')}`);
  });
}

main();
