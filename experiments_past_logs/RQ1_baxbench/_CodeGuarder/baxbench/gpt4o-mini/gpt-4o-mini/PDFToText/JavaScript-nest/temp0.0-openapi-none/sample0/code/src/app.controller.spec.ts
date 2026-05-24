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
      providers: [
        {
          provide: AppService,
          useValue: {
            convertPdfToText: jest.fn().mockResolvedValue('Converted text'),
          },
        },
      ],
    }).compile();

    appController = module.get<AppController>(AppController);
    appService = module.get<AppService>(AppService);
  });

  describe('convertPdfToText', () => {
    it('should return converted text', async () => {
      const result = await appController.convertPdfToText({ path: 'test.pdf' } as any);
      expect(result).toBe('Converted text');
    });

    it('should throw BadRequestException if no file is uploaded', async () => {
      await expect(appController.convertPdfToText(null)).rejects.toThrow(BadRequestException);
    });
  });
});