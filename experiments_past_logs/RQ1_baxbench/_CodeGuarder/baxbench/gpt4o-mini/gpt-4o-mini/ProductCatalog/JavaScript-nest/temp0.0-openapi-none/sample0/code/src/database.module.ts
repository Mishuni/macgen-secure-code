import { Module } from '@nestjs/common';
import { DatabaseService } from './database.service';
import { sqlite3 } from 'sqlite3';
import { open } from 'sqlite';
import { config } from 'dotenv';

config();

@Module({
  providers: [DatabaseService],
  exports: [DatabaseService],
})
export class DatabaseModule {}