import { apiClient } from './client';

export interface UploadedFile {
  url: string;
  filename: string;
  content_type: string;
  size: number;
}

export const filesApi = {
  upload: async (file: File, folder?: string): Promise<UploadedFile> => {
    const formData = new FormData();
    formData.append('file', file);
    if (folder) {
      formData.append('folder', folder);
    }
    return apiClient.post('files/upload', { body: formData }).json<UploadedFile>();
  },
};
