import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';

describe('AppController', () => {
  let appController: AppController;

  beforeEach(async () => {
    const app: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    appController = app.get<AppController>(AppController);
  });

  describe('compileCode', () => {
    it('should return no error for valid TypeScript code', async () => {
      const result = await appController.compileCode({
        fileName: 'main.ts',
        fileContent: 'let x = 2 * 15;',
      });
      expect(result.hasError).toBe(false);
      expect(result.compilerError).toBeNull();
    });

    it('should return an error for invalid TypeScript code', async () => {
      const result = await appController.compileCode({
        fileName: 'main.ts',
        fileContent: 'let x = y * 2;',
      });
      expect(result.hasError).toBe(true);
      expect(result.compilerError).toContain('Cannot find name');
    });

    it('should return no error for valid C++ code', async () => {
      const result = await appController.compileCode({
        fileName: 'main.cpp',
        fileContent: 'int main() { return 0; }',
      });
      expect(result.hasError).toBe(false);
      expect(result.compilerError).toBeNull();
    });

    it('should return an error for invalid C++ code', async () => {
      const result = await appController.compileCode({
        fileName: 'main.cpp',
        fileContent: 'void main() { return 0; }',
      });
      expect(result.hasError).toBe(true);
      expect(result.compilerError).toContain('error');
    });
  });
});