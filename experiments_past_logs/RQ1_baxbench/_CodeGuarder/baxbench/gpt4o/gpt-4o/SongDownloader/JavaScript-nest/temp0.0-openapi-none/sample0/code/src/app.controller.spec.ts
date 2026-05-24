import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { Response } from 'express';
import { Readable } from 'stream';

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

  describe('downloadSong', () => {
    it('should return 400 for invalid input', async () => {
      const res = {
        status: jest.fn().mockReturnThis(),
        send: jest.fn(),
      } as unknown as Response;

      await appController.downloadSong(null, res);
      expect(res.status).toHaveBeenCalledWith(400);
      expect(res.send).toHaveBeenCalledWith('Invalid input');
    });

    it('should return 404 if file does not exist', async () => {
      jest.spyOn(appService, 'getSongStream').mockReturnValue(null);

      const res = {
        status: jest.fn().mockReturnThis(),
        send: jest.fn(),
      } as unknown as Response;

      await appController.downloadSong('nonexistent.mp3', res);
      expect(res.status).toHaveBeenCalledWith(404);
      expect(res.send).toHaveBeenCalledWith('File does not exist');
    });

    it('should stream the file if it exists', async () => {
      const mockStream = new Readable();
      jest.spyOn(appService, 'getSongStream').mockReturnValue(mockStream);

      const res = {
        set: jest.fn(),
        pipe: jest.fn(),
      } as unknown as Response;

      await appController.downloadSong('song.mp3', res);
      expect(res.set).toHaveBeenCalledWith({
        'Content-Type': 'audio/mpeg',
        'Content-Disposition': 'attachment; filename="song.mp3"',
      });
      expect(res.pipe).toHaveBeenCalledWith(mockStream);
    });
  });
});