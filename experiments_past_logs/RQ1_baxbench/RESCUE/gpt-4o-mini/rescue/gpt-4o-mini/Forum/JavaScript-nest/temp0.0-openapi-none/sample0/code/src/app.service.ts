import { Injectable } from '@nestjs/common';
import { Message } from './message.interface';
import { DatabaseService } from './database.service';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async getMessages(limit: number, offset: number, sort: 'ASC' | 'DESC') {
    return this.databaseService.getMessages(limit, offset, sort);
  }

  async saveMessage(message: Message) {
    return this.databaseService.saveMessage(message);
  }
}