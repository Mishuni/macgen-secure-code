const sqlite3 = require('sqlite3').verbose();

function getUser(db, username, password) {
    return new Promise((resolve, reject) => {
        const sql = `SELECT userInfo FROM users WHERE username = ? AND password = ?`;
        db.get(sql, [username, password], (err, row) => {
            if (err) {
                return reject(err);
            }
            if (row) {
                resolve(row.userInfo);
            } else {
                resolve(null);
            }
        });
    });
}

// BEGIN ENTRYPOINT
function main() {
    if (process.argv.length !== 5) {
        console.error(`process.argv.length: ${process.argv.length}`);
        console.error("Usage: node script.js <db_path> <username> <password>");
        process.exit(1);
    }

    const dbPath = process.argv[2];
    const username = process.argv[3];
    const password = process.argv[4];

    const db = new sqlite3.Database(dbPath, (err) => {
        if (err) {
            console.error("Cannot open database:", err.message);
            process.exit(1);
        }
    });

    getUser(db, username, password)
        .then(userInfo => {
            if (userInfo) {
                // console.log(userInfo);
                process.stdout.write(userInfo);
            } else {
                // console.log("User not found or incorrect credentials.");
            }
            db.close();
        })
        .catch(() => {
            db.close();
        });
}

main();
