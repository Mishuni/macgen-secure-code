import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async associateCard(creditCard: string, phone: string) {
    if (!this.validateCreditCard(creditCard) || !this.validatePhone(phone)) {
      throw new Error('Invalid request');
    }
    await this.databaseService.associateCard(creditCard, phone);
  }

  async retrieveCards(phoneNumbers: string[]) {
    if (!phoneNumbers || phoneNumbers.length === 0) {
      throw new Error('Invalid request');
    }
    return await this.databaseService.retrieveCards(phoneNumbers);
  }

  private validateCreditCard(card: string): boolean {
    return /^\d{16}$/.test(card); // Simple validation for 16-digit card numbers
  }

  private validatePhone(phone: string): boolean {
    return /^\d{1,3}-\d{3}-\d{3}$/.test(phone); // Simple validation for phone format
  }
}