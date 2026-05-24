import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { Express } from 'express';

describe('AppController', () => {
  let appController: AppController;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = app.get<AppController>(AppController);
  });

  describe('upload', () => {
    it('should return an image ID', async () => {
      const file: Express.Multer.File = {
        fieldname: 'file',
        originalname: 'test.png',
        encoding: '7bit',
        mimetype: 'image/png',
        size: 1024,
        buffer: Buffer.from(''),
        destination: '',
        filename: '',
        path: '',
        stream: null,
      };
      const result = await appController.uploadImage(file);
      expect(result).toHaveProperty('id');
    });
  });

  describe('getImage', () => {
    it('should return an image buffer', async () => {
      const imageId = 'test-id';
      const result = await appController.getImage(imageId);
      expect(result).toBeInstanceOf(Buffer);
    });
  });
});