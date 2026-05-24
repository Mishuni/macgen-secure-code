import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { MulterModule } from '@nestjs/platform-express';

@Module({
  imports: [MulterModule.register({
    limits: {
      fileSize: 10 * 1024 * 1024, // Limit file size to 10MB
    },
  })],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}