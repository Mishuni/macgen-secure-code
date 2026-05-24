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

    describe('searchFiles', () => {
        it('should return an array of files', async () => {
            const result = { files: ['/data/files/file1.txt'] };
            jest.spyOn(appController['appService'], 'searchFiles').mockImplementation(async () => result);

            expect(await appController.searchFiles({ search_content: 'Hello' })).toBe(result);
        });
    });
});