import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { MulterModule } from '@nestjs/platform-express';

@Module({
  imports: [
    MulterModule.register({
      dest: '/tmp',
      limits: {
        fileSize: 5 * 1024 * 1024, // Limit to 5MB
      },
    }),
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}