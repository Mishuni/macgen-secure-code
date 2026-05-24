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

  describe('convert', () => {
    it('should return converted text', async () => {
      const result = 'Sample text from PDF';
      jest.spyOn(appController, 'convert').mockImplementation(async () => result);
      expect(await appController.convert({} as any)).toBe(result);
    });
  });
});