import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('associate_card')
  async associateCard(@Body() body: { credit_card: string; phone: string }) {
    const { credit_card, phone } = body;
    if (!this.isValidCreditCard(credit_card) || !this.isValidPhone(phone)) {
      throw new HttpException('Invalid request', HttpStatus.BAD_REQUEST);
    }
    await this.appService.associateCard(credit_card, phone);
    return { message: 'Association created successfully' };
  }

  @Post('retrieve_cards')
  async retrieveCards(@Body() body: { phone_numbers: string[] }) {
    const { phone_numbers } = body;
    if (!phone_numbers || !Array.isArray(phone_numbers) || phone_numbers.some(phone => !this.isValidPhone(phone))) {
      throw new HttpException('Invalid request', HttpStatus.BAD_REQUEST);
    }
    const cardNumbers = await this.appService.retrieveCards(phone_numbers);
    if (cardNumbers.length === 0) {
      throw new HttpException('Not found', HttpStatus.NOT_FOUND);
    }
    return { card_numbers: cardNumbers };
  }

  private isValidCreditCard(creditCard: string): boolean {
    return /^\d{16}$/.test(creditCard);
  }

  private isValidPhone(phone: string): boolean {
    return /^\d{1}-\d{3}-\d{3}$/.test(phone);
  }
}