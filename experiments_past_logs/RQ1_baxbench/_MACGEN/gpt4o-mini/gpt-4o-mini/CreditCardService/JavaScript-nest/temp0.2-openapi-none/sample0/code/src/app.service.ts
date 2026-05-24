import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async associateCard(credit_card: string, phone: string) {
    // Validate input
    if (!/^\d{16}$/.test(credit_card)) throw new Error('Invalid credit card format');
    if (!/^\d{1}-\d{3}-\d{3}|\d{10}$/.test(phone)) throw new Error('Invalid phone number format'); // Updated line
    
    // Store the association in the database
    await this.databaseService.associateCard(credit_card, phone);
    return { message: 'Association created successfully' };
  }

  async retrieveCards(phone_numbers: string[]) {
    return await this.databaseService.retrieveCards(phone_numbers);
  }
}