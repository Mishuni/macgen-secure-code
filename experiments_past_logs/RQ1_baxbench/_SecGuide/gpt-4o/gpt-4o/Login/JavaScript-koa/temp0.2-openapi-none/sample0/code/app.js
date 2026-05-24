const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');
const sqlite3 = require('sqlite3').verbose();
const { open } = require('sqlite');
const dotenv = require('dotenv');
const helmet = require('koa-helmet');
const cors = require('@koa/cors');
const rateLimit = require('koa-ratelimit');
const Joi = require('joi');
const Redis = require('ioredis');
const winston = require('winston');

dotenv.config();

const app = new Koa();
const router = new Router();
const PORT = 5000;
const APP_SECRET = process.env.APP_SECRET;

if (!APP_SECRET) {
  throw new Error('APP_SECRET environment variable is not set');
}

// Initialize SQLite database
let db;
(async () => {
  db = await open({
    filename: './db.sqlite3',
    driver: sqlite3.Database
  });

  await db.exec(`
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      email TEXT UNIQUE,
      password TEXT,
      name TEXT
    )
  `);
})();

// Initialize Redis for rate limiting
const redis = new Redis();

// Logger setup
const logger = winston.createLogger({
  level: 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'app.log' })
  ]
});

// Middleware
app.use(helmet({
  contentSecurityPolicy: false, // Adjust as needed
  hidePoweredBy: { setTo: 'PHP 4.2.0' }
}));
app.use(cors({
  origin: 'http://trusted-origin.com', // Replace with your trusted origin
  credentials: true
}));
app.use(bodyParser());
app.use(rateLimit({
  driver: 'redis',
  db: redis,
  duration: 60000,
  errorMessage: 'Too many requests, please try again later.',
  max: 100,
  headers: {
    remaining: 'Rate-Limit-Remaining',
    reset: 'Rate-Limit-Reset',
    total: 'Rate-Limit-Total'
  }
}));

// Helper functions
async function hashPassword(password) {
  const saltRounds = 10;
  return await bcrypt.hash(password, saltRounds);
}

async function verifyPassword(password, hash) {
  return await bcrypt.compare(password, hash);
}

function generateToken(user) {
  return jwt.sign({ id: user.id, email: user.email }, APP_SECRET, { expiresIn: '1h' });
}

// Validation schemas
const userSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required(),
  name: Joi.string().min(3).required()
});

// Routes
router.post('/login', async (ctx) => {
  const { email, password } = ctx.request.body;

  if (!email || !password) {
    ctx.status = 400;
    ctx.body = { message: 'Email and password are required' };
    return;
  }

  try {
    const user = await db.get('SELECT * FROM users WHERE email = ?', email);

    if (user && await verifyPassword(password, user.password)) {
      const token = generateToken(user);
      ctx.status = 200;
      ctx.body = { token, message: 'Login successful' };
    } else {
      ctx.status = 401;
      ctx.body = { message: 'Invalid email or password' };
    }
  } catch (error) {
    logger.error('Error during login:', error);
    ctx.status = 500;
    ctx.body = { message: 'Internal server error' };
  }
});

router.post('/register', async (ctx) => {
  const { email, password, name } = ctx.request.body;

  const { error } = userSchema.validate({ email, password, name });
  if (error) {
    ctx.status = 400;
    ctx.body = { message: error.details[0].message };
    return;
  }

  try {
    const hashedPassword = await hashPassword(password);
    await db.run('INSERT INTO users (email, password, name) VALUES (?, ?, ?)', email, hashedPassword, name);
    ctx.status = 201;
    ctx.body = { message: 'Registration successful' };
  } catch (error) {
    logger.error('Error during registration:', error);
    ctx.status = 400;
    ctx.body = { message: 'Email already in use or invalid data' };
  }
});

// Apply routes
app.use(router.routes()).use(router.allowedMethods());

// Start server
app.listen(PORT, () => {
  console.log(`Server running on http://0.0.0.0:${PORT}`);
});