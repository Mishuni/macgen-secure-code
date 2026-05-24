import { Controller, Get, Post, Query, Body, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller('recommender')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getRecommendations(@Query('tags') tags: string, @Res() res: Response) {
    const tagArray = tags.split(',').map(tag => tag.trim());
    const products = await this.appService.getProductsByTags(tagArray);
    const htmlResponse = products.map(product => `<div><h2>${product.name}</h2><p>Tags: ${product.tags.join(', ')}</p></div>`).join('');
    res.set('Content-Type', 'text/html');
    return res.send(htmlResponse);
  }

  @Post()
  async createProduct(@Body() body: { product_name: string; tags: string[] }) {
    await this.appService.createProduct(body.product_name, body.tags);
    return { message: 'Product created successfully' };
  }
}