import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { Response } from 'express';

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

  describe('download', () => {
    it('should return 400 if filename is not provided', async () => {
      const response = {
        status: jest.fn().mockReturnThis(),
        send: jest.fn(),
      } as unknown as Response;
      await appController.download({ filename: '' }, response);
      expect(response.status).toHaveBeenCalledWith(400);
    });

    it('should return 404 if file does not exist', async () => {
      jest.spyOn(appService, 'getFileStream').mockResolvedValue(null);
      const response = {
        status: jest.fn().mockReturnThis(),
        send: jest.fn(),
      } as unknown as Response;
      await appController.download({ filename: 'nonexistent.mp3' }, response);
      expect(response.status).toHaveBeenCalledWith(404);
    });
  });
});