import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { HttpStatus } from '@nestjs/common';
import { Response } from 'express';

describe('AppController', () => {
  let appController: AppController;
  let mockResponse: Partial<Response>;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = module.get<AppController>(AppController);
    mockResponse = {
      set: jest.fn(),
      status: jest.fn().mockReturnThis(),
      send: jest.fn(),
      pipe: jest.fn(),
    };
  });

  it('should return 404 if file does not exist', async () => {
    const result = await appController.downloadSong({ filename: 'nonexistent.mp3' }, mockResponse as Response);
    expect(mockResponse.status).toHaveBeenCalledWith(HttpStatus.NOT_FOUND);
    expect(mockResponse.send).toHaveBeenCalledWith('File does not exist');
  });
});