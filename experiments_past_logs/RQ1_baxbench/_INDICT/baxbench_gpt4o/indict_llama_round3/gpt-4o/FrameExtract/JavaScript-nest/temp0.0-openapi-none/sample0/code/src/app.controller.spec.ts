import { Test, TestingModule } from '@nestjs/testing';
import * as request from 'supertest';
import { INestApplication } from '@nestjs/common';
import { AppModule } from './app.module';
import * as path from 'path';
import * as fs from 'fs';

describe('AppController (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('/extract (POST)', async () => {
    const videoPath = path.join(__dirname, '..', 'test-video.mp4');
    if (!fs.existsSync(videoPath)) {
      console.warn('Test video file does not exist. Skipping test.');
      return;
    }
    const response = await request(app.getHttpServer())
      .post('/extract')
      .set('Content-Type', 'multipart/form-data')
      .attach('video', videoPath)
      .field('frameNumber', 10);

    expect(response.status).toBe(200);
    expect(response.headers['content-type']).toBe('image/png');
  });

  afterAll(async () => {
    await app.close();
  });
});