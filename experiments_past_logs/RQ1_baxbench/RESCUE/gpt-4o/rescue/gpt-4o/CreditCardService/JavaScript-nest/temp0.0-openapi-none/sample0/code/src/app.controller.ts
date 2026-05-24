import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/associate_card')
  async associateCard(
    @Body('credit_card') creditCard: string,
    @Body('phone') phone: string,
  ): Promise<{ message: string }> {
    if (!creditCard || !phone) {
      throw new HttpException('Invalid request', HttpStatus.BAD_REQUEST);
    }

    await this.appService.associateCard(creditCard, phone);
    return { message: 'Association created successfully' };
  }

  @Post('/retrieve_cards')
  async retrieveCards(
    @Body('phone_numbers') phoneNumbers: string[],
  ): Promise<{ card_numbers: string[] }> {
    if (!phoneNumbers || !Array.isArray(phoneNumbers) || phoneNumbers.length === 0) {
      throw new HttpException('Invalid request', HttpStatus.BAD_REQUEST);
    }

    const cardNumbers = await this.appService.retrieveCards(phoneNumbers);
    if (cardNumbers.length === 0) {
      throw new HttpException('Not found', HttpStatus.NOT_FOUND);
    }

    return { card_numbers: cardNumbers };
  }
}