import { Controller, Get, Post, Query, Body, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller('recommender')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getRecommendations(@Query('tags') tags: string, @Res() res: Response) {
    const tagList = tags.split(',').map(tag => tag.trim());
    const products = await this.appService.getProductsByTags(tagList);
    const htmlResponse = this.appService.generateHtmlResponse(products);
    res.set('Content-Type', 'text/html');
    return res.status(HttpStatus.OK).send(htmlResponse);
  }

  @Post()
  async postProduct(@Body() body: { product_name: string; tags: string[] }, @Res() res: Response) {
    if (!body.product_name || !Array.isArray(body.tags)) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
    }
    await this.appService.addProduct(body.product_name, body.tags);
    return res.status(HttpStatus.OK).send('Product added successfully');
  }
}