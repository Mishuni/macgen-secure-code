import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { NotFoundException, BadRequestException } from '@nestjs/common';

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

  describe('extractFrame', () => {
    it('should throw BadRequestException if no file is uploaded', async () => {
      await expect(appController.extractFrame(null, 10)).rejects.toThrow(BadRequestException);
    });

    it('should throw BadRequestException if frame number is invalid', async () => {
      await expect(appController.extractFrame({ path: 'dummy/path' } as any, -1)).rejects.toThrow(BadRequestException);
    });

    it('should throw NotFoundException if frame cannot be extracted', async () => {
      jest.spyOn(appService, 'extractFrame').mockRejectedValue(new NotFoundException());
      await expect(appController.extractFrame({ path: 'dummy/path' } as any, 10)).rejects.toThrow(NotFoundException);
    });
  });
});