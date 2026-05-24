import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import * as dotenv from 'dotenv';
import * as express from 'express';

async function bootstrap() {
  dotenv.config();
  const app = await NestFactory.create(AppModule);

  // Serve static files for profile photos
  app.use('/uploads', express.static('uploads'));

  await app.listen(5000, '0.0.0.0');
  console.log('Application is running on http://0.0.0.0:5000');
}
bootstrap();