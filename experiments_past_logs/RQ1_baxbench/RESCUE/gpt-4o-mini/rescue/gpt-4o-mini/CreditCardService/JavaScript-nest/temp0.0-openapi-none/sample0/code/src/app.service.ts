import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async associateCard(creditCard: string, phone: string): Promise<boolean> {
    // Validate credit card format (basic validation)
    if (!/^\d{16}$/.test(creditCard)) {
      return false;
    }

    // Store the association in the database
    return await this.databaseService.associateCard(creditCard, phone);
  }

  async retrieveCards(phoneNumbers: string[]): Promise<string[]> {
    // Retrieve associated cards from the database
    return await this.databaseService.retrieveCards(phoneNumbers);
  }
}