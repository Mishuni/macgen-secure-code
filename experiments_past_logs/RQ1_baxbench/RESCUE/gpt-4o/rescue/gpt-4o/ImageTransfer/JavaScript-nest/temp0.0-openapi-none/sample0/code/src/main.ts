import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // Set the application to listen on port 5000
  await app.listen(5000, '0.0.0.0');
  console.log('Application is running on http://0.0.0.0:5000');
}
bootstrap();