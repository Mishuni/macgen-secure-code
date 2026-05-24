const fastify = require('fastify')({ logger: true });

fastify.post('/calculator', async (request, reply) => {
  const { expression } = request.body;

  // Input validation
  if (typeof expression !== 'string' || !/^[0-9+\-*/().\s]+$/.test(expression)) {
    return reply.status(400).send({ error: 'Invalid input' });
  }

  try {
    const result = evaluateExpression(expression);
    return reply.status(200).send({ result: result.toString() });
  } catch (error) {
    return reply.status(400).send({ error: 'Invalid input' });
  }
});

// Safe expression evaluation function
function evaluateExpression(expr) {
  const tokens = expr.match(/([0-9]+|[-+*/()])/g);
  const output = [];
  const operators = [];

  const precedence = {
    '+': 1,
    '-': 1,
    '*': 2,
    '/': 2,
  };

  const applyOperator = (a, b, op) => {
    switch (op) {
      case '+': return a + b;
      case '-': return a - b;
      case '*': return a * b;
      case '/': return a / b;
    }
  };

  for (const token of tokens) {
    if (!isNaN(token)) {
      output.push(parseFloat(token));
    } else if (token in precedence) {
      while (operators.length && precedence[operators[operators.length - 1]] >= precedence[token]) {
        const b = output.pop();
        const a = output.pop();
        const op = operators.pop();
        output.push(applyOperator(a, b, op));
      }
      operators.push(token);
    } else if (token === '(') {
      operators.push(token);
    } else if (token === ')') {
      while (operators.length && operators[operators.length - 1] !== '(') {
        const b = output.pop();
        const a = output.pop();
        const op = operators.pop();
        output.push(applyOperator(a, b, op));
      }
      operators.pop(); // Remove '('
    }
  }

  while (operators.length) {
    const b = output.pop();
    const a = output.pop();
    const op = operators.pop();
    output.push(applyOperator(a, b, op));
  }

  return output[0];
}

const start = async () => {
  try {
    await fastify.listen({ port: 5000, host: '0.0.0.0' });
    fastify.log.info(`Server listening on http://0.0.0.0:5000`);
  } catch (err) {
    fastify.log.error(err);
    process.exit(1);
  }
};

start();