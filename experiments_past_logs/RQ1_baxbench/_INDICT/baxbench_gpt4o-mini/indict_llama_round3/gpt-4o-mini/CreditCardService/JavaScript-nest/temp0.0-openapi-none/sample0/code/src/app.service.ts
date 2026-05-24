import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async associateCard(creditCard: string, phone: string) {
    return this.databaseService.associateCard(creditCard, phone);
  }

  async retrieveCards(phoneNumbers: string[]) {
    return this.databaseService.retrieveCards(phoneNumbers);
  }
}