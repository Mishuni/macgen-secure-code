import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { MulterModule } from '@nestjs/platform-express';

@Module({
  imports: [
    MulterModule.register({
      dest: './uploads', // Ensure this directory is non-executable
    }),
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}