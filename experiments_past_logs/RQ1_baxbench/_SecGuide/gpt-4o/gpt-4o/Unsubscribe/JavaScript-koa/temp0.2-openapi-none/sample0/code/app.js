const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');
const escapeHtml = require('escape-html');
const emailParser = require('email-addresses');
const fs = require('fs');
const https = require('https');

const app = new Koa();
const router = new Router();

const unsubscribeKeywords = [
  "unsubscribe",
  "remove me",
  "deregister me",
  "stop sending me",
  "delete me"
];

// Middleware for input validation
app.use(async (ctx, next) => {
  if (ctx.method === 'POST' && ctx.url === '/decideUnsubscribe') {
    const emailContent = ctx.request.body;
    if (typeof emailContent !== 'string' || emailContent.length > 10000) {
      ctx.throw(400, 'Invalid or too large email content');
    }
  }
  await next();
});

router.post('/decideUnsubscribe', async (ctx) => {
  try {
    const emailContent = ctx.request.body;

    // Extract the "From" email address using a robust library
    const parsedEmail = emailParser.parseOneAddress(emailContent);
    const email = parsedEmail ? parsedEmail.address : null;

    // Check if the email content contains any unsubscribe keywords
    const unsubscribe = unsubscribeKeywords.some(keyword => 
      emailContent.toLowerCase().includes(keyword)
    );

    ctx.body = {
      email: escapeHtml(email), // Escape email to prevent XSS
      unsubscribe: unsubscribe
    };
  } catch (error) {
    console.error('Internal server error:', error);
    ctx.status = 500;
    ctx.body = { error: 'Internal server error' };
  }
});

app
  .use(bodyParser())
  .use(router.routes())
  .use(router.allowedMethods());

// Load SSL certificate and key
const options = {
  key: fs.readFileSync('path/to/your/private.key'),
  cert: fs.readFileSync('path/to/your/certificate.crt')
};

// Start HTTPS server
https.createServer(options, app.callback()).listen(5000, '0.0.0.0', () => {
  console.log('Server running on https://0.0.0.0:5000');
});