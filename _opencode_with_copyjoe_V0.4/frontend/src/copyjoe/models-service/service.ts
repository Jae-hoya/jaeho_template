import axios from "axios"

import type {
  CopyGenerateResponse,
  CopyLiteRequest,
  CopyLiteResponse,
  FileUploadResponse,
  LandingAnalyzeRequest,
  LandingAnalyzeResponse,
  RagIndexResponse,
  RagResetResponse,
} from "./types"

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000",
  timeout: 180000,
})

export async function generateCopy(payload: CopyLiteRequest): Promise<CopyLiteResponse> {
  const response = await api.post<CopyLiteResponse>("/api/v1/copy/generate", payload)
  return response.data
}

export async function analyzeLanding(payload: LandingAnalyzeRequest): Promise<LandingAnalyzeResponse> {
  const response = await api.post<LandingAnalyzeResponse>("/api/v1/web/landing/analyze", payload)
  return response.data
}

export async function exportCopyDocx(payload: {
  file_name: string
  result: CopyGenerateResponse
}): Promise<Blob> {
  const response = await api.post("/api/v1/export/docx", payload, {
    responseType: "blob",
  })
  return response.data
}

export async function exportCopyMarkdown(payload: {
  file_name: string
  result: CopyGenerateResponse
}): Promise<Blob> {
  const response = await api.post("/api/v1/export/md", payload, {
    responseType: "blob",
  })
  return response.data
}

export async function exportCopyDoc(payload: {
  file_name: string
  result: CopyGenerateResponse
}): Promise<Blob> {
  const response = await api.post("/api/v1/export/doc", payload, {
    responseType: "blob",
  })
  return response.data
}

export async function getHealth(): Promise<Record<string, unknown>> {
  const response = await api.get("/health")
  return response.data
}

export async function uploadSourceFiles(files: File[]): Promise<FileUploadResponse> {
  const formData = new FormData()
  for (const file of files) {
    formData.append("files", file)
  }

  const response = await api.post<FileUploadResponse>("/api/v1/files/upload", formData, {
    timeout: 600000,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  })
  return response.data
}

export async function indexRagDocuments(
  documentIds: string[],
  options?: { chunk_size?: number; chunk_overlap?: number }
): Promise<RagIndexResponse> {
  const response = await api.post<RagIndexResponse>("/api/v1/rag/index", {
    document_ids: documentIds,
    chunk_size: options?.chunk_size ?? 700,
    chunk_overlap: options?.chunk_overlap ?? 120,
  })
  return response.data
}

export async function resetRagIndex(): Promise<RagResetResponse> {
  const response = await api.post<RagResetResponse>("/api/v1/rag/reset")
  return response.data
}
