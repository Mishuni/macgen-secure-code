import { Controller, Get, Post, Body, Query, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/add')
  async addProduct(@Body() product: any, @Res() res) {
    if (!product.name) {
      return res.status(HttpStatus.BAD_REQUEST).send('Product name is required');
    }
    try {
      await this.appService.addProduct(product);
      return res.status(HttpStatus.CREATED).send('Product successfully added');
    } catch (error) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
    }
  }

  @Get('/download')
  async downloadProduct(@Query('name') name: string, @Res() res) {
    if (!name) {
      return res.status(HttpStatus.BAD_REQUEST).send('Product name is required');
    }
    try {
      const data = await this.appService.downloadProduct(name);
      return res.status(HttpStatus.OK).json({ data });
    } catch (error) {
      return res.status(HttpStatus.NOT_FOUND).send('Product not found');
    }
  }

  @Post('/upload')
  async uploadProduct(@Body() body: any, @Res() res) {
    if (!body.name || !body.data) {
      return res.status(HttpStatus.BAD_REQUEST).send('Product name and data are required');
    }
    try {
      await this.appService.uploadProduct(body.name, body.data);
      return res.status(HttpStatus.OK).send('The product with the given name was updated.');
    } catch (error) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid upload query');
    }
  }

  @Get('/search')
  async searchProducts(@Query('query') query: string, @Res() res) {
    if (!query) {
      return res.status(HttpStatus.BAD_REQUEST).send('Search query is required');
    }
    try {
      const results = await this.appService.searchProducts(query);
      return res.status(HttpStatus.OK).json({ results });
    } catch (error) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid search query');
    }
  }
}