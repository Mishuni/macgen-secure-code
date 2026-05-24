import { Controller, Get, Post, Query, Body, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller('recommender')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getRecommendations(@Query('tags') tags: string, @Res() res: Response) {
    const tagArray = tags.split(',').map(tag => tag.trim());
    const products = await this.appService.getProductsByTags(tagArray);
    res.status(HttpStatus.OK).send(products);
  }

  @Post()
  async postProduct(@Body() productData: { product_name: string; tags: string[] }, @Res() res: Response) {
    if (!productData.product_name || !Array.isArray(productData.tags) || productData.tags.length === 0) {
      return res.status(HttpStatus.BAD_REQUEST).send({ message: 'Invalid input' });
    }
    try {
      await this.appService.addProduct(productData.product_name, productData.tags);
      res.status(HttpStatus.OK).send({ message: 'Product added successfully' });
    } catch (error) {
      res.status(HttpStatus.BAD_REQUEST).send({ message: 'Invalid input' });
    }
  }
}