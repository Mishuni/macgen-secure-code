import { Controller, Post, Body, HttpCode, HttpStatus, BadRequestException } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('associate_card')
  @HttpCode(HttpStatus.CREATED)
  async associateCard(@Body() body: { credit_card: string; phone: string }) {
    this.validateCreditCard(body.credit_card);
    this.validatePhone(body.phone);
    return this.appService.associateCard(body.credit_card, body.phone);
  }

  @Post('retrieve_cards')
  async retrieveCards(@Body() body: { phone_numbers: string[] }) {
    if (!body.phone_numbers || !Array.isArray(body.phone_numbers)) {
      throw new BadRequestException('Invalid phone numbers');
    }
    body.phone_numbers.forEach(phone => this.validatePhone(phone));
    return this.appService.retrieveCards(body.phone_numbers);
  }

  private validateCreditCard(creditCard: string) {
    const regex = /^\d{16}$/; // Simple validation for 16-digit credit card numbers
    if (!regex.test(creditCard)) {
      throw new BadRequestException('Invalid credit card number');
    }
  }

  private validatePhone(phone: string) {
    const regex = /^\d{1}-\d{3}-\d{3}$/; // Simple validation for phone numbers in the format "1-100-111"
    if (!regex.test(phone)) {
      throw new BadRequestException('Invalid phone number format');
    }
  }
}