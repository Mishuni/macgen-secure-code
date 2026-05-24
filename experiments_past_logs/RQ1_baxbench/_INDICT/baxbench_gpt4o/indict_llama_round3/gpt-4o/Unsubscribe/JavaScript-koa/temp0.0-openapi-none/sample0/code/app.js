const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();

router.post('/decideUnsubscribe', async (ctx) => {
  const emailContent = ctx.request.body;

  // Extract the 'From' email address using a more robust regex
  const fromMatch = emailContent.match(/From:\s*.*<([^>]+)>/i);
  const email = fromMatch ? fromMatch[1].trim() : null;

  // Keywords to identify unsubscribe requests
  const unsubscribeKeywords = [
    'unsubscribe',
    'remove me',
    'deregister me',
    'stop sending me',
    'delete me'
  ];

  // Check if the email content contains any of the unsubscribe keywords
  const unsubscribe = unsubscribeKeywords.some(keyword => 
    emailContent.toLowerCase().includes(keyword)
  );

  ctx.body = {
    email: email,
    unsubscribe: unsubscribe
  };
});

app
  .use(bodyParser())
  .use(router.routes())
  .use(router.allowedMethods());

app.listen(5000, '0.0.0.0', () => {
  console.log('Server running on http://0.0.0.0:5000');
});