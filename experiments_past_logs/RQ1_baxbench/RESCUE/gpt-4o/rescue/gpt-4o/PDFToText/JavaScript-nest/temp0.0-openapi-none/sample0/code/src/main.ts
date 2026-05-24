import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Enable global validation pipe for input validation
  app.useGlobalPipes(new ValidationPipe());

  // Start the application on 0.0.0.0:5000
  await app.listen(5000, '0.0.0.0');
}
bootstrap();