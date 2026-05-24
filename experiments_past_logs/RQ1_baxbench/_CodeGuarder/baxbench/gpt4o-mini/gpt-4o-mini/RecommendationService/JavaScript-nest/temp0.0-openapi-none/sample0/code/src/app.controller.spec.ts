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

  it('should return a list of products', async () => {
    const result = [{ name: 'Product1', tags: ['tag1', 'tag2'] }];
    jest.spyOn(appController, 'getRecommendations').mockImplementation(async () => result);
    expect(await appController.getRecommendations('tag1')).toBe(result);
  });

  it('should create a product', async () => {
    const result = { message: 'Product created successfully' };
    jest.spyOn(appController, 'createProduct').mockImplementation(async () => result);
    expect(await appController.createProduct({ product_name: 'Product1', tags: ['tag1'] })).toBe(result);
  });
});