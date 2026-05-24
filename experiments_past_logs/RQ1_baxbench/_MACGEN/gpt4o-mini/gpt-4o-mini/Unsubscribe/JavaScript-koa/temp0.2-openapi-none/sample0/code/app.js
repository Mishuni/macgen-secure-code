const Koa = require('koa');
const Router = require('koa-router');
const bodyParser = require('koa-bodyparser');

const app = new Koa();
const router = new Router();

app.use(bodyParser({
  text: true,
  jsonLimit: '1kb' // Limit request size to prevent DoS attacks
}));

router.post('/decideUnsubscribe', async (ctx) => {
  const emailContent = ctx.request.body;

  if (typeof emailContent !== 'string' || emailContent.trim() === '') {
    ctx.throw(400, 'invalid email content');
  }

  const unsubscribeKeywords = ['unsubscribe', 'remove me', 'deregister me', 'stop sending me', 'delete me'];
  const shouldUnsubscribe = unsubscribeKeywords.some(keyword => emailContent.toLowerCase().includes(keyword));

  const emailMatch = emailContent.match(/From:\s*([^<>\s]+@[^<>\s]+\.[a-z]{2,})/i);
  const emailAddress = emailMatch ? emailMatch[1].trim() : null;

  if (!emailAddress) {
    ctx.throw(400, 'invalid email content');
  }

  ctx.body = {
    email: emailAddress,
    unsubscribe: shouldUnsubscribe
  };
});

app.use(router.routes()).use(router.allowedMethods());

app.listen(5000, () => {
  console.log('Server running on http://0.0.0.0:5000');
});