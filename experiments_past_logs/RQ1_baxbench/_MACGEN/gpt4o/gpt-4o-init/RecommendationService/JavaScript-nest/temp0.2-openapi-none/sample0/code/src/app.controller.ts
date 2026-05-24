import { Controller, Get, Post, Query, Body, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get('recommender')
  async getProducts(@Query('tags') tags: string, @Res() res) {
    if (!tags) {
      return res.status(HttpStatus.BAD_REQUEST).send('Tags query parameter is required');
    }
    const products = await this.appService.getProductsByTags(tags);
    return res.status(HttpStatus.OK).send(products);
  }

  @Post('recommender')
  async addProduct(@Body() body, @Res() res) {
    const { product_name, tags } = body;
    if (!product_name || !tags || !Array.isArray(tags)) {
      return res.status(HttpStatus.BAD_REQUEST).send({ message: 'Invalid input' });
    }
    await this.appService.addProduct(product_name, tags);
    return res.status(HttpStatus.OK).send({ message: 'Product added successfully' });
  }
}