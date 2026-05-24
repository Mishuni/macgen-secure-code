export interface Entry {
  id: string;
  title: string;
  content: string;
  lastModifiedBy: string;
  lastModifiedAt: string;
}

export interface NewEntry {
  title: string;
  content: string;
  createdBy: string;
}

export interface UpdateEntry {
  content: string;
  modifiedBy: string;
  summary?: string;
}