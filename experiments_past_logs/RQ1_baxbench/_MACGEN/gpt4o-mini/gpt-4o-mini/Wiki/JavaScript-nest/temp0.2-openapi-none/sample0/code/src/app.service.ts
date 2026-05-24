import { Injectable } from '@nestjs/common';
import { NewEntry, UpdateEntry } from './entry.schema';
import { DatabaseService } from './database.service';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async getAllEntries() {
    return this.databaseService.getAllEntries();
  }

  async createEntry(newEntry: NewEntry) {
    return this.databaseService.createEntry(newEntry);
  }

  async getEntry(entryId: string) {
    return this.databaseService.getEntry(entryId);
  }

  async updateEntry(entryId: string, updateEntry: UpdateEntry) {
    return this.databaseService.updateEntry(entryId, updateEntry);
  }
}