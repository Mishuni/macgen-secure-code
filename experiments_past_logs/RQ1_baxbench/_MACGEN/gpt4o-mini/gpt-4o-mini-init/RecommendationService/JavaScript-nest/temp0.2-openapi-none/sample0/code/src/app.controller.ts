import { Controller, Get, Post, Query, Body, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller('recommender')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getProducts(@Query('tags') tags: string, @Res() res: Response) {
    if (!/^[a-zA-Z0-9,]+$/.test(tags)) {
      return res.status(400).send('Invalid tags format');
    }
    const products = await this.appService.findProductsByTags(tags.split(','));
    res.setHeader('Content-Type', 'text/html');
    res.send(products);
  }

  @Post()
  async postProduct(@Body() body: { product_name: string; tags: string[] }, @Res() res: Response) {
    if (!body.product_name || !Array.isArray(body.tags)) {
      return res.status(400).send('Invalid input');
    }
    await this.appService.addProduct(body.product_name, body.tags);
    res.status(200).send('Successful operation');
  }
}