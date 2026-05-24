const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const multer = require('@koa/multer');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

const app = new Koa();
const router = new Router();
const upload = multer({ 
    dest: 'uploads/',
    fileFilter: (req, file, cb) => {
        const allowedTypes = ['image/png', 'image/jpeg'];
        if (allowedTypes.includes(file.mimetype)) {
            cb(null, true);
        } else {
            cb(new Error('File type not allowed'), false);
        }
    }
});

// Initialize SQLite database
const db = new sqlite3.Database('db.sqlite3', (err) => {
    if (err) {
        console.error('Error opening database ' + err.message);
    } else {
        db.run(`CREATE TABLE IF NOT EXISTS profiles (
            username TEXT PRIMARY KEY,
            profile_page TEXT,
            profile_photo TEXT
        )`);
    }
});

// Middleware to handle multipart/form-data
app.use(bodyParser());

// Route to add a new user profile
router.post('/add_profile', upload.fields([{ name: 'profile_page' }, { name: 'profile_photo' }]), async (ctx) => {
    const { username } = ctx.request.body;
    const profilePage = ctx.files['profile_page'] ? ctx.files['profile_page'][0].path : null;
    const profilePhoto = ctx.files['profile_photo'] ? ctx.files['profile_photo'][0].path : null;

    if (!username || !profilePage || !profilePhoto) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid input' };
        return;
    }

    // Validate username
    const usernameRegex = /^[a-zA-Z0-9]{3,20}$/; // Alphanumeric, 3-20 characters
    if (!usernameRegex.test(username)) {
        ctx.status = 400;
        ctx.body = { error: 'Invalid username format' };
        return;
    }

    db.get('SELECT username FROM profiles WHERE username = ?', [username], (err, row) => {
        if (err) {
            ctx.status = 500;
            ctx.body = { error: 'Database error' };
            return;
        }
        if (row) {
            ctx.status = 403;
            ctx.body = { error: 'Profile already exists, creation forbidden' };
            return;
        }

        db.run('INSERT INTO profiles (username, profile_page, profile_photo) VALUES (?, ?, ?)', [username, profilePage, profilePhoto], function (err) {
            if (err) {
                ctx.status = 500;
                ctx.body = { error: 'Database error' };
                return;
            }
            ctx.status = 201;
            ctx.body = { message: 'Profile created successfully' };
        });
    });
});

// Route to get user profile
router.get('/profile/:username', async (ctx) => {
    const { username } = ctx.params;

    db.get('SELECT profile_page FROM profiles WHERE username = ?', [username], (err, row) => {
        if (err) {
            ctx.status = 500;
            ctx.body = { error: 'Database error' };
            return;
        }
        if (!row) {
            ctx.status = 404;
            ctx.body = { error: 'Profile not found' };
            return;
        }

        // Validate the file path
        const profilePagePath = path.resolve(row.profile_page);
        if (!profilePagePath.startsWith(path.resolve('uploads'))) {
            ctx.status = 403;
            ctx.body = { error: 'Access to the requested file is forbidden' };
            return;
        }

        ctx.status = 200;
        ctx.type = 'html';
        ctx.body = fs.readFileSync(profilePagePath, 'utf8');
    });
});

// Route to get user profile photo
router.get('/profile-photo/:username', async (ctx) => {
    const { username } = ctx.params;

    db.get('SELECT profile_photo FROM profiles WHERE username = ?', [username], (err, row) => {
        if (err) {
            ctx.status = 500;
            ctx.body = { error: 'Database error' };
            return;
        }
        if (!row) {
            ctx.status = 404;
            ctx.body = { error: 'Profile photo not found' };
            return;
        }

        // Validate the file path
        const profilePhotoPath = path.resolve(row.profile_photo);
        if (!profilePhotoPath.startsWith(path.resolve('uploads'))) {
            ctx.status = 403;
            ctx.body = { error: 'Access to the requested file is forbidden' };
            return;
        }

        ctx.status = 200;
        ctx.type = 'image/png';
        ctx.body = fs.createReadStream(profilePhotoPath);
    });
});

// Use the router
app.use(router.routes()).use(router.allowedMethods());

// Start the server
app.listen(5000, () => {
    console.log('Server is running on http://0.0.0.0:5000');
});