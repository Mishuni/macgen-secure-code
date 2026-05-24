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