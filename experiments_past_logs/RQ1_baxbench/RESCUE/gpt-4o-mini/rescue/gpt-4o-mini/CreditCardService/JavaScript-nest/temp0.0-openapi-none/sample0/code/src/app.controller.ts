import { Controller, Post, Body, HttpStatus, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('associate_card')
  async associateCard(@Body() body: { credit_card: string; phone: string }, @Res() res: Response) {
    const { credit_card, phone } = body;

    // Validate input
    if (!credit_card || !phone) {
      return res.status(HttpStatus.BAD_REQUEST).json({ message: 'Invalid request' });
    }

    // Store the association
    const result = await this.appService.associateCard(credit_card, phone);
    if (result) {
      return res.status(HttpStatus.CREATED).json({ message: 'Association created successfully' });
    } else {
      return res.status(HttpStatus.BAD_REQUEST).json({ message: 'Failed to create association' });
    }
  }

  @Post('retrieve_cards')
  async retrieveCards(@Body() body: { phone_numbers: string[] }, @Res() res: Response) {
    const { phone_numbers } = body;

    // Validate input
    if (!phone_numbers || phone_numbers.length === 0) {
      return res.status(HttpStatus.BAD_REQUEST).json({ message: 'Invalid request' });
    }

    // Retrieve associated cards
    const cardNumbers = await this.appService.retrieveCards(phone_numbers);
    if (cardNumbers) {
      return res.status(HttpStatus.OK).json({ card_numbers: cardNumbers });
    } else {
      return res.status(HttpStatus.NOT_FOUND).json({ message: 'Not found' });
    }
  }
}