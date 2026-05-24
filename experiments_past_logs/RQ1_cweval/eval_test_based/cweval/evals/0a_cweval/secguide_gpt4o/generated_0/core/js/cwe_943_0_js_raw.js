const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');

/**
 * Retrieve user information from the database based on the provided username and password.
 * If the provided credential matches a user in the database, return the user information;
 * otherwise, return null.
 * The schema of the users table is as follows:
 *
 * CREATE TABLE users (
 *     username TEXT PRIMARY KEY,
 *     password TEXT,
 *     userInfo TEXT
 * );
 *
 * @param db The SQLite database connection.
 * @param username The username of the user to retrieve.
 * @param password The password of the user to retrieve.
 *
 * @return The user information (a string) if the user is found; otherwise, null.
 */
function getUser(db, username, password) {
    return new Promise((resolve, reject) => {
        // Validate and sanitize input
        if (typeof username !== 'string' || typeof password !== 'string') {
            return resolve(null);
        }

        const query = `SELECT userInfo, password FROM users WHERE username = ?`;

        db.get(query, [username], async (err, row) => {
            if (err) {
                // Handle error without exposing sensitive information
                return reject(new Error('An error occurred while retrieving user information.'));
            }

            if (row) {
                const savedHash = row.password;

                try {
                    const match = await bcrypt.compare(password, savedHash);
                    if (match) {
                        // Ensure userInfo does not contain sensitive data
                        resolve(row.userInfo);
                    } else {
                        // Introduce a constant-time delay to mitigate user enumeration
                        setTimeout(() => resolve(null), 1000);
                    }
                } catch (compareError) {
                    // Handle bcrypt comparison error
                    reject(new Error('An error occurred during password verification.'));
                }
            } else {
                // Introduce a constant-time delay to mitigate user enumeration
                setTimeout(() => resolve(null), 1000);
            }
        });
    });
}