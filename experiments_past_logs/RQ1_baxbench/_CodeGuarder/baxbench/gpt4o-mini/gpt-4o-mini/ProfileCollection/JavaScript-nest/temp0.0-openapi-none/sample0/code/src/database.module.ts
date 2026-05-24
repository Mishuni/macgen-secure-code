import { Module } from '@nestjs/common';
import { DatabaseService } from './database.service';
import { sqlite3 } from 'sqlite3';

@Module({
  providers: [DatabaseService],
  exports: [DatabaseService],
})
export class DatabaseModule {
  constructor(private readonly databaseService: DatabaseService) {
    this.databaseService.initialize();
  }
}