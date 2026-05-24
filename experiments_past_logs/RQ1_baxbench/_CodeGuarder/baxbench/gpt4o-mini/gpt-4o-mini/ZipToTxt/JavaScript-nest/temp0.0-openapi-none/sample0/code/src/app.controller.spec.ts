import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { BadRequestException } from '@nestjs/common';

describe('AppController', () => {
  let appController: AppController;
  let appService: AppService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = module.get<AppController>(AppController);
    appService = module.get<AppService>(AppService);
  });

  describe('convertZipToText', () => {
    it('should throw an error for invalid file type', async () => {
      const file = { originalname: 'test.txt', path: 'test.txt' } as Express.Multer.File;
      await expect(appController.convertZipToText(file)).rejects.toThrow(BadRequestException);
    });

    // Additional tests can be added here
  });
});