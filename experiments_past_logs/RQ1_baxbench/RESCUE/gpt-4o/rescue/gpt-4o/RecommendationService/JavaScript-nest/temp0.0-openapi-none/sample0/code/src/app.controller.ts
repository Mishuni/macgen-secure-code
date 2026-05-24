import { Controller, Get, Post, Query, Body, Res, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get('/recommender')
  async getRecommendations(@Query('tags') tags: string, @Res() res: Response) {
    if (!tags) {
      throw new HttpException('Tags query parameter is required', HttpStatus.BAD_REQUEST);
    }

    const tagList = tags.split(',').map((tag) => tag.trim());
    const products = await this.appService.getProductsByTags(tagList);

    let htmlResponse = '<html><body><h1>Recommended Products</h1><ul>';
    products.forEach((product) => {
      htmlResponse += `<li>${product.product_name}</li>`;
    });
    htmlResponse += '</ul></body></html>';

    res.setHeader('Content-Type', 'text/html');
    res.send(htmlResponse);
  }

  @Post('/recommender')
  async postProduct(@Body() body: { product_name: string; tags: string[] }) {
    if (!body.product_name || !body.tags || !Array.isArray(body.tags)) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }

    await this.appService.addProduct(body.product_name, body.tags);
    return { message: 'Product added successfully' };
  }
}