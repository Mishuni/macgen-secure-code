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

  describe('concatenatePDFs', () => {
    it('should throw BadRequestException if no files are provided', async () => {
      await expect(appController.concatenatePDFs([], null)).rejects.toThrow(BadRequestException);
    });

    // Additional tests can be added here
  });
});