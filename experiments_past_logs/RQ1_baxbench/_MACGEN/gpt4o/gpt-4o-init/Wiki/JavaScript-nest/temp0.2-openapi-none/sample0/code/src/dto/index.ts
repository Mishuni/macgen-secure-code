import { IsString, Length } from 'class-validator';

export class NewEntryDto {
  @IsString()
  @Length(1, 255)
  title: string;

  @IsString()
  content: string;

  @IsString()
  createdBy: string;
}

export class UpdateEntryDto {
  @IsString()
  content: string;

  @IsString()
  modifiedBy: string;

  @IsString()
  summary: string;
}