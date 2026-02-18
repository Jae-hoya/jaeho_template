export type Objective = "brand_memory" | "click" | "add_to_cart" | "consultation"

export type Style = "head" | "body" | "cta" | "slogan" | "sns" | "description"

export interface CopyGenerateRequest {
  product_name: string
  target_audience: string
  pain_point: string
  differentiator: string
  tone: string
  objective: Objective
  styles: Style[]
  channel: string
  language: string
  web_search_mode: boolean
  use_rag: boolean
  top_k: number
}

export interface SourceItem {
  source_type: "rag" | "web"
  title?: string
  url?: string
  snippet: string
}

export interface CopyGenerateResponse {
  head: string
  body: string
  cta: string
  slogan: string
  sns: string
  description: string
  storyboard_outline: string[]
  rationale: string
  sources: SourceItem[]
}

export interface CopyLiteRequest {
  prompt: string
  styles: Style[]
  language?: string
  objective?: Objective | null
  channel?: string | null
  landing_url?: string | null
  landing_query?: string | null
  web_search_mode?: boolean
  use_rag?: boolean
  top_k?: number
}

export interface CopyLiteResponse {
  assistant_message: string
  assumptions: string[]
  normalized_request: CopyGenerateRequest
  result: CopyGenerateResponse
}

export interface LandingAnalyzeRequest {
  url?: string | null
  query?: string | null
  max_results?: number
}

export interface LandingAnalyzeResponse {
  url: string
  title: string
  h1: string[]
  h2: string[]
  cta_buttons: string[]
  body: string
  from_tavily: boolean
}

export interface UploadedFileItem {
  file_name: string
  document_id?: string | null
  success: boolean
  text_length: number
  error_code?: string | null
  error_message?: string | null
}

export interface FileUploadResponse {
  total_files: number
  success_count: number
  failed_count: number
  files: UploadedFileItem[]
}

export interface RagIndexResponse {
  indexed_documents: number
  indexed_chunks: number
  missing_document_ids: string[]
}
