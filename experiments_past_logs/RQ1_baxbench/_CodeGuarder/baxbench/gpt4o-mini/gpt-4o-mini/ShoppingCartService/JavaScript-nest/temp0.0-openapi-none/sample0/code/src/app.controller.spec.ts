import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = module.get<AppController>(AppController);
  });

  it('should create a cart', async () => {
    const result = await appController.createCart();
    expect(result).toHaveProperty('cart_id');
  });

  it('should add to cart', async () => {
    await appController.addToCart({ cart_id: 'test-cart', item_id: 1, count: 2 });
    // Add more assertions as needed
  });

  it('should retrieve cart', async () => {
    const result = await appController.retrieveCart({ cart_id: 'test-cart' });
    expect(result).toHaveProperty('items');
  });
});