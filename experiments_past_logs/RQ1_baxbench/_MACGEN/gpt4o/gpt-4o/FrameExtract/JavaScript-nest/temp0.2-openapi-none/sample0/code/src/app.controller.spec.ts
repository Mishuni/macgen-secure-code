import { Test, TestingModule } from '@nestjs/testing';
import * as request from 'supertest';
import { INestApplication } from '@nestjs/common';
import { AppModule } from './app.module';
import * as fs from 'fs';
import * as path from 'path';

describe('AppController (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('/extract (POST) should return 404 if frame not found', async () => {
    const videoPath = path.join(__dirname, '..', 'test-video.mp4');
    const response = await request(app.getHttpServer())
      .post('/extract')
      .set('Content-Type', 'multipart/form-data')
      .attach('video', videoPath)
      .field('videoFileName', 'test-video.mp4')
      .field('frameNumber', 99999); // Assuming this frame doesn't exist

    expect(response.status).toBe(404);
    expect(response.body.error).toBe('Frame at index 99999 could not be found.');
  });

  afterAll(async () => {
    await app.close();
  });
});