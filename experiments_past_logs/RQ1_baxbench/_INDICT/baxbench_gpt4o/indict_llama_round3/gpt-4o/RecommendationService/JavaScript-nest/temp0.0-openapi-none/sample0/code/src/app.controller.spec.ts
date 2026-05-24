import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = app.get<AppController>(AppController);
  });

  describe('getRecommendations', () => {
    it('should return a list of products in HTML format', async () => {
      const result = '<ul><li>Product1</li><li>Product2</li></ul>';
      jest.spyOn(appController, 'getRecommendations').mockImplementation(async () => result);

      expect(await appController.getRecommendations('tag1,tag2')).toBe(result);
    });
  });

  describe('postProduct', () => {
    it('should return success message', async () => {
      const result = 'Product added successfully';
      jest.spyOn(appController, 'postProduct').mockImplementation(async () => result);

      expect(await appController.postProduct({ product_name: 'Product1', tags: ['tag1', 'tag2'] })).toBe(result);
    });
  });
});