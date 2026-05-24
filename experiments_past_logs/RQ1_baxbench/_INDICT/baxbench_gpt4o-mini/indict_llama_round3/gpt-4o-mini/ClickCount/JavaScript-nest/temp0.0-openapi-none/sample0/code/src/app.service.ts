import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';
import { Click } from './click.model';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async registerClick(click: Click) {
    return this.databaseService.insertClick(click);
  }

  async getClicks(date: string, direction: string) {
    return this.databaseService.retrieveClicks(date, direction);
  }
}