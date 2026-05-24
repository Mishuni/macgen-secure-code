export class NewEntry {
  title: string;
  content: string;
  createdBy: string;
}

export class UpdateEntry {
  content: string;
  modifiedBy: string;
  summary?: string;
}