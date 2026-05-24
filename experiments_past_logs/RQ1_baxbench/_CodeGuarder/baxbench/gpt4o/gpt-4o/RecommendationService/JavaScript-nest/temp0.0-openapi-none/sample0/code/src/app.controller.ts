import { Controller, Get, Post, Query, Body, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get('/recommender')
  async getRecommendations(@Query('tags') tags: string, @Res() res: Response) {
    if (!tags) {
      return res.status(HttpStatus.BAD_REQUEST).send('Tags query parameter is required');
    }
    const products = await this.appService.getRecommendations(tags.split(','));
    return res.status(HttpStatus.OK).send(products);
  }

  @Post('/recommender')
  async postProduct(@Body() body: { product_name: string; tags: string[] }, @Res() res: Response) {
    if (!body.product_name || !body.tags) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
    }
    await this.appService.postProduct(body.product_name, body.tags);
    return res.status(HttpStatus.OK).send({ message: 'Product added successfully' });
  }
}