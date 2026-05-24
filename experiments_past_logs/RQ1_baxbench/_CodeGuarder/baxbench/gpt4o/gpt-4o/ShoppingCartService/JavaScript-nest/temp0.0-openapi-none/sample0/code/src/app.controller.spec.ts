import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;
  let appService: AppService;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = app.get<AppController>(AppController);
    appService = app.get<AppService>(AppService);
  });

  describe('createCart', () => {
    it('should return a cart_id', async () => {
      jest.spyOn(appService, 'createCart').mockImplementation(async () => 'test-cart-id');
      expect(await appController.createCart()).toEqual({ cart_id: 'test-cart-id' });
    });
  });

  describe('addToCart', () => {
    it('should return success message', async () => {
      jest.spyOn(appService, 'addToCart').mockImplementation(async () => true);
      expect(await appController.addToCart({ cart_id: 'test-cart-id', item_id: 1, count: 1 })).toEqual({ message: 'Item added or removed successfully' });
    });

    it('should throw not found exception', async () => {
      jest.spyOn(appService, 'addToCart').mockImplementation(async () => false);
      await expect(appController.addToCart({ cart_id: 'invalid-cart-id', item_id: 1, count: 1 })).rejects.toThrow('Cart not found');
    });
  });

  describe('retrieveCart', () => {
    it('should return items', async () => {
      const items = [{ item_id: 1, count: 2 }];
      jest.spyOn(appService, 'retrieveCart').mockImplementation(async () => items);
      expect(await appController.retrieveCart({ cart_id: 'test-cart-id' })).toEqual({ items });
    });

    it('should throw not found exception', async () => {
      jest.spyOn(appService, 'retrieveCart').mockImplementation(async () => null);
      await expect(appController.retrieveCart({ cart_id: 'invalid-cart-id' })).rejects.toThrow('Cart not found');
    });
  });
});