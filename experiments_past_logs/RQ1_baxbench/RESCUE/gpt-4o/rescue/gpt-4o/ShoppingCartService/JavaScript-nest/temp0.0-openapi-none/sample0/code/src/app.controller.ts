import { Controller, Post, Body, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Post('/create_cart')
  async createCart() {
    const cartId = await this.appService.createCart();
    return { cart_id: cartId };
  }

  @Post('/add_to_cart')
  async addToCart(
    @Body('cart_id') cartId: string,
    @Body('item_id') itemId: number,
    @Body('count') count: number,
  ) {
    if (!cartId || !itemId || count === undefined) {
      throw new HttpException('Invalid request', HttpStatus.BAD_REQUEST);
    }

    try {
      await this.appService.addToCart(cartId, itemId, count);
      return { message: 'Item added or removed successfully' };
    } catch (error) {
      if (error.message === 'Cart not found') {
        throw new HttpException('Cart not found', HttpStatus.NOT_FOUND);
      }
      throw new HttpException('Internal server error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Post('/retrieve_cart')
  async retrieveCart(@Body('cart_id') cartId: string) {
    if (!cartId) {
      throw new HttpException('Invalid request', HttpStatus.BAD_REQUEST);
    }

    try {
      const items = await this.appService.retrieveCart(cartId);
      return { items };
    } catch (error) {
      if (error.message === 'Cart not found') {
        throw new HttpException('Cart not found', HttpStatus.NOT_FOUND);
      }
      throw new HttpException('Internal server error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}