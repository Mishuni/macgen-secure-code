import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;

  const mockAppService = {
    extractFrame: jest.fn().mockResolvedValue(Buffer.from('mockImageBuffer')),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [
        {
          provide: AppService,
          useValue: mockAppService,
        },
      ],
    }).compile();

    appController = module.get<AppController>(AppController);
  });

  it('should extract a frame', async () => {
    const result = await appController.extractFrame({ path: 'mockPath' } as any, 132, {} as any);
    expect(result).toBeDefined();
  });

  it('should handle frame not found error', async () => {
    mockAppService.extractFrame.mockRejectedValue(new Error('Frame at index 132 could not be found.'));
    await expect(appController.extractFrame({ path: 'mockPath' } as any, 132, {} as any)).rejects.toThrow('Frame at index 132 could not be found.');
  });
});