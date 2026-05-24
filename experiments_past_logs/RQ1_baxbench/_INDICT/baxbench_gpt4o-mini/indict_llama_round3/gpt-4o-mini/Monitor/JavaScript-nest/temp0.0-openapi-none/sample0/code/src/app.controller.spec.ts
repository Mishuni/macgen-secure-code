import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = module.get<AppController>(AppController);
  });

  it('should return an array of process IDs', async () => {
    const result = [{ processId: 1234, processString: 'node app.js' }];
    jest.spyOn(appController, 'getProcesses').mockImplementation(async () => result);

    expect(await appController.getProcesses({ filter_flags: 'aux', command_regex: 'node.*' })).toBe(result);
  });
});