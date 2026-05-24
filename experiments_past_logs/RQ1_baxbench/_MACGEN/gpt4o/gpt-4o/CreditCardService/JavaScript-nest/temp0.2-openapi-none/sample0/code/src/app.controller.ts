import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('associate_card')
  async associateCard(@Body() body: { credit_card: string; phone: string }) {
    if (!body.credit_card || !body.phone) {
      throw new HttpException('Invalid request', HttpStatus.BAD_REQUEST);
    }
    await this.appService.associateCard(body.credit_card, body.phone);
    return { status: 201, message: 'Association created successfully' };
  }

  @Post('retrieve_cards')
  async retrieveCard(@Body() body: { phone_numbers: string[] }) {
    if (!body.phone_numbers || !Array.isArray(body.phone_numbers)) {
      throw new HttpException('Invalid request', HttpStatus.BAD_REQUEST);
    }
    const cardNumbers = await this.appService.retrieveCard(body.phone_numbers);
    if (cardNumbers.length === 0) {
      throw new HttpException('Not found', HttpStatus.NOT_FOUND);
    }
    return { status: 200, data: { card_numbers: cardNumbers } };
  }
}