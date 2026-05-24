import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Set the application to listen on 0.0.0.0:5000
  await app.listen(5000, '0.0.0.0');
}
bootstrap();