import axios from "axios";

export const BACKEND_ORIGIN = "http://localhost:8000";

const api = axios.create({
  baseURL: `${BACKEND_ORIGIN}/api/v1`,
});

export const toAbsoluteMediaUrl = (path) => {
  if (!path) return "";
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  return `${BACKEND_ORIGIN}${path}`;
};

export const uploadMedia = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const getSummary = (mediaId) => api.get(`/summary/${mediaId}`);
export const askQuestion = (mediaId, question) => api.post("/chat", { media_id: mediaId, question });
export const getTimestamps = (mediaId, topic) => api.post("/timestamps", { media_id: mediaId, topic });
