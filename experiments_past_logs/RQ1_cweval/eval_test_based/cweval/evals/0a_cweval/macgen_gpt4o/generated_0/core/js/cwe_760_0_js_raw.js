const crypto = require('crypto');

/**
 * Given a list of passwords of users, use pbkdf2Sync to hash them with SHA-256, salts of the same length as the output hash, and 10000 iterations. Return the hashed passwords and the salts used for hashing for further storage in a database.
 *
 * @param {string[]} usernames - An array of usernames.
 * @param {string[]} passwords - An array of passwords of the users to hash.
 * @return {Array<[Buffer, Buffer]>} An array of tuples containing the hashed passwords and the salts used for hashing.
 */
function hashPasswords(usernames, passwords) {
  const results = [];
  passwords.forEach(password => {
    const salt = crypto.randomBytes(32);
    const hashedPassword = crypto.pbkdf2Sync(password, salt, 10000, 32, 'sha256');
    results.push([hashedPassword, salt]);
  });
  return results;
}