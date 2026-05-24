export class NewEntryDto {
  title: string;
  content: string;
  createdBy: string;
}

export class UpdateEntryDto {
  content: string;
  modifiedBy: string;
  summary: string;
}