import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';
import { NewEntry, UpdateEntry } from './entry.dto';

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

  async getEntryEdits(entryId: string) {
    return this.databaseService.getEntryEdits(entryId);
  }
}