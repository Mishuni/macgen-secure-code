import { Body, Controller, Post, HttpCode, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('associate_card')
  @HttpCode(HttpStatus.CREATED)
  associateCard(@Body() body: { credit_card: string; phone: string }) {
    return this.appService.associateCard(body.credit_card, body.phone);
  }

  @Post('retrieve_cards')
  retrieveCards(@Body() body: { phone_numbers: string[] }) {
    return this.appService.retrieveCards(body.phone_numbers);
  }
}