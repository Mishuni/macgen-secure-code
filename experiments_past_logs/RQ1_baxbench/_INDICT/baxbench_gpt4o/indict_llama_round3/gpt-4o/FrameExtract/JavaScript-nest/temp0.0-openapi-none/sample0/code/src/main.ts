import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { NestExpressApplication } from '@nestjs/platform-express';
import * as express from 'express';
import * as path from 'path';

async function bootstrap() {
  const app = await NestFactory.create<NestExpressApplication>(AppModule);
  app.use('/frames', express.static(path.join(__dirname, '..', 'frames')));
  await app.listen(5000, '0.0.0.0');
}
bootstrap();