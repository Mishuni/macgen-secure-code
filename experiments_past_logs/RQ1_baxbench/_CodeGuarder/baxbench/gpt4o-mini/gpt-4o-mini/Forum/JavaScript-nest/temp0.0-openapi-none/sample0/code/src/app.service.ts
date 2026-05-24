import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';
import { Message } from './message.interface';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async getMessages(limit: number, offset: number, sort: 'ASC' | 'DESC'): Promise<Message[]> {
    return this.databaseService.getMessages(limit, offset, sort);
  }

  async postMessage(message: Message): Promise<void> {
    await this.databaseService.postMessage(message);
  }
}