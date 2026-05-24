import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { HttpStatus } from '@nestjs/common';

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

  it('should return 400 for invalid filename', async () => {
    const response = await appController.downloadSong({ filename: 'invalid_file' }, { status: jest.fn().mockReturnThis(), send: jest.fn() });
    expect(response).toBeUndefined();
  });

  it('should return 404 for non-existing file', async () => {
    jest.spyOn(appService, 'getSongStream').mockImplementation(() => { throw new Error('File does not exist'); });
    const response = await appController.downloadSong({ filename: 'non_existing_song.mp3' }, { status: jest.fn().mockReturnThis(), send: jest.fn() });
    expect(response).toBeUndefined();
  });
});