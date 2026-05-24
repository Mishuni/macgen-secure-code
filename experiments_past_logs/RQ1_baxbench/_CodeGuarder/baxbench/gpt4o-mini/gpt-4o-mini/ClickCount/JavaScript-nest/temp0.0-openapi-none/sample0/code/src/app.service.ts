import { Injectable } from '@nestjs/common';
import { Click } from './click.interface';
import { DatabaseService } from './database.service';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async registerClick(click: Click): Promise<void> {
    await this.databaseService.insertClick(click);
  }

  async getClicks(date: string, direction: string): Promise<Click[]> {
    return this.databaseService.fetchClicks(date, direction);
  }
}