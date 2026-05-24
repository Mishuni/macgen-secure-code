import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import * as request from 'supertest';
import { INestApplication } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

describe('AppController', () => {
  let app: INestApplication;
  let appController: AppController;

  beforeAll(async () => {
    const moduleRef: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    app = moduleRef.createNestApplication();
    await app.init();
    appController = moduleRef.get<AppController>(AppController);
  });

  it('should upload an image and return an ID', async () => {
    const filePath = path.join(__dirname, '../test-image.jpg');
    const response = await request(app.getHttpServer())
      .post('/upload')
      .attach('file', filePath);

    expect(response.status).toBe(200);
    expect(response.body).toHaveProperty('id');
  });

  it('should return 404 for non-existent image', async () => {
    const response = await request(app.getHttpServer()).get('/images/nonexistent-id');
    expect(response.status).toBe(404);
  });

  afterAll(async () => {
    await app.close();
  });
});