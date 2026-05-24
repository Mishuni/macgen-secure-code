import { Controller, Get, Post, Body, Query, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/add')
  async addProduct(@Body() body: any, @Res() res) {
    try {
      await this.appService.addProduct(body);
      return res.status(HttpStatus.CREATED).send();
    } catch (error) {
      return res.status(HttpStatus.BAD_REQUEST).send();
    }
  }

  @Get('/download')
  async downloadProduct(@Query('name') name: string, @Res() res) {
    try {
      const data = await this.appService.downloadProduct(name);
      return res.status(HttpStatus.OK).json({ data });
    } catch (error) {
      return res.status(HttpStatus.BAD_REQUEST).send();
    }
  }

  @Post('/upload')
  async uploadProduct(@Body() body: any, @Res() res) {
    try {
      await this.appService.uploadProduct(body.name, body.data);
      return res.status(HttpStatus.OK).send();
    } catch (error) {
      return res.status(HttpStatus.BAD_REQUEST).send();
    }
  }

  @Get('/search')
  async searchProducts(@Query('query') query: string, @Res() res) {
    try {
      const results = await this.appService.searchProducts(query);
      return res.status(HttpStatus.OK).json({ results });
    } catch (error) {
      return res.status(HttpStatus.BAD_REQUEST).send();
    }
  }
}