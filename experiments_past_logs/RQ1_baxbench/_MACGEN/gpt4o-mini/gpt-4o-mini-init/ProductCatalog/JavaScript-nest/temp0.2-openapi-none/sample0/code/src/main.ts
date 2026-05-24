import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  app.enableCors(); // Optional: can be configured if needed
  await app.listen(5000, '0.0.0.0');
}
bootstrap();