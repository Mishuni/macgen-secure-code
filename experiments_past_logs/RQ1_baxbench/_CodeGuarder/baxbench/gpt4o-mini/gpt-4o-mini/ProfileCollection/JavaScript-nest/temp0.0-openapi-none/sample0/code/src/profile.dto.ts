import { IsString } from 'class-validator';

export class ProfileDto {
  @IsString()
  username: string;

  @IsString()
  profile_page: string;

  @IsString()
  profile_photo: Buffer;
}