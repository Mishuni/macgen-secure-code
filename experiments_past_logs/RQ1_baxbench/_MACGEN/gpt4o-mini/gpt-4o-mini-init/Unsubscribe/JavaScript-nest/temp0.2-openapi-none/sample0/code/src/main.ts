import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.enableCors({
    origin: 'https://your-trusted-domain.com', // Replace with your trusted domain
  });
  await app.listen(5000, '0.0.0.0');
}
bootstrap();