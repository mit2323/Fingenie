import api from './api'

export const documentService = {
  upload: (file: File) => {
    const data = new FormData()
    data.append('file', file)
    return api.post('/knowledge/upload', data, { headers: { 'Content-Type': 'multipart/form-data' } }).then((response) => response.data)
  },
}
