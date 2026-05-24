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
    const moduleFixture: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
    appController = moduleFixture.get<AppController>(AppController);
  });

  it('should create a GIF successfully', async () => {
    const response = await request(app.getHttpServer())
      .post('/create-gif')
      .attach('images', fs.readFileSync(path.join(__dirname, '../test/image1.jpg')), 'image1.jpg')
      .attach('images', fs.readFileSync(path.join(__dirname, '../test/image2.jpg')), 'image2.jpg')
      .field('targetSize', '500x500')
      .field('delay', 100)
      .field('appendReverted', true)
      .expect(200);

    expect(response.headers['content-type']).toBe('image/gif');
  });

  afterAll(async () => {
    await app.close();
  });
});