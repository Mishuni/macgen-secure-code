import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import * as request from 'supertest';
import { INestApplication } from '@nestjs/common';
import { join } from 'path';
import { existsSync, mkdirSync } from 'fs';

describe('AppController', () => {
  let app: INestApplication;
  let appService = { saveFile: jest.fn(), getFilePath: jest.fn() };

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [{ provide: AppService, useValue: appService }],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('/upload (POST)', async () => {
    const uploadDir = join(process.cwd(), 'uploads');
    if (!existsSync(uploadDir)) {
      mkdirSync(uploadDir);
    }

    appService.saveFile.mockResolvedValue('test-image.jpg');

    return request(app.getHttpServer())
      .post('/upload')
      .attach('file', join(__dirname, '..', 'test-image.jpg'))
      .expect(200)
      .expect({ id: 'test-image.jpg' });
  });

  it('/images/:imageId (GET)', async () => {
    appService.getFilePath.mockResolvedValue(join(process.cwd(), 'uploads', 'test-image.jpg'));

    return request(app.getHttpServer())
      .get('/images/test-image.jpg')
      .expect(200);
  });

  afterAll(async () => {
    await app.close();
  });
});