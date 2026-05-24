import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { DatabaseModule } from './database.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  await DatabaseModule.initializeDatabase();
  await app.listen(5000);
}
bootstrap();