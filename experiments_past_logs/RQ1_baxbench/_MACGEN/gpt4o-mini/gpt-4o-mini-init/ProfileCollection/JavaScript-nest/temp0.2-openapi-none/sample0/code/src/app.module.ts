import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { MulterModule } from '@nestjs/platform-express';
import { DatabaseModule } from './database.module';

@Module({
  imports: [MulterModule.register(), DatabaseModule],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}