import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { BadRequestException, InternalServerErrorException } from '@nestjs/common';

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
            extractTextFromPdf: jest.fn(),
          },
        },
      ],
    }).compile();

    appController = module.get<AppController>(AppController);
    appService = module.get<AppService>(AppService);
  });

  it('should return text from PDF', async () => {
    const mockText = 'This is a sample text from PDF.';
    jest.spyOn(appService, 'extractTextFromPdf').mockResolvedValue(mockText);

    const result = await appController.convertPdfToText({ path: 'mock.pdf' } as any, {} as any);
    expect(result).toBe(mockText);
  });

  it('should throw BadRequestException if no file is uploaded', async () => {
    await expect(appController.convertPdfToText(null, {} as any)).rejects.toThrow(BadRequestException);
  });

  it('should throw InternalServerErrorException on conversion failure', async () => {
    jest.spyOn(appService, 'extractTextFromPdf').mockRejectedValue(new Error('Conversion failed.'));
    await expect(appController.convertPdfToText({ path: 'mock.pdf' } as any, {} as any)).rejects.toThrow(InternalServerErrorException);
  });
});