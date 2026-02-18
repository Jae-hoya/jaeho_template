<script setup lang="ts">
import { isAxiosError } from "axios"
import { ref } from "vue"

import PromptSection from "../copyjoe/sections/PromptSection.vue"
import GenerationSection from "../copyjoe/sections/GenerationSection.vue"
import { generateCopy, indexRagDocuments, resetRagIndex, uploadSourceFiles } from "../copyjoe/models-service/service"
import { webAgentService } from "../copyjoe/models-service/WebAgentService"
import type {
  CopyGenerateRequest,
  CopyGenerateResponse,
  CopyLiteRequest,
  LandingAnalyzeRequest,
  LandingAnalyzeResponse,
  Style,
} from "../copyjoe/models-service/types"

type UploadStatus = {
  level: "success" | "warning" | "error"
  title: string
  details: string[]
}

const loadingCopy = ref(false)
const loadingLanding = ref(false)
const loadingUpload = ref(false)
const errorMessage = ref("")
const uploadStatus = ref<UploadStatus | null>(null)

const result = ref<CopyGenerateResponse | null>(null)
const landing = ref<LandingAnalyzeResponse | null>(null)
const turns = ref<Array<{ role: "user" | "assistant"; text: string }>>([])
const generationRound = ref(0)
const selectedStyles = ref<Style[]>(["head", "body", "cta", "slogan", "sns", "description"])
const currentRagDocumentIds = ref<string[]>([])

const lastGenerationContext = ref<CopyGenerateRequest | null>(null)

function addTurn(role: "user" | "assistant", text: string) {
  turns.value.push({ role, text })
}

function toError(error: unknown): string {
  if (isAxiosError(error)) {
    const status = error.response?.status
    const payload = error.response?.data as
      | {
          detail?: string | Array<{ loc?: Array<string | number>; msg?: string }>
          error?: { message?: string }
        }
      | undefined

    if (status === 422 && Array.isArray(payload?.detail)) {
      const fieldErrors = payload.detail
        .map((item) => {
          const loc = Array.isArray(item.loc) ? String(item.loc[item.loc.length - 1]) : "unknown"
          const msg = item.msg || "invalid value"
          return `${loc}: ${msg}`
        })
        .join(" | ")

      return `입력값을 이해하지 못한 항목이 있어요 -> ${fieldErrors}`
    }

    if (payload?.error?.message) {
      return payload.error.message
    }

    if (typeof payload?.detail === "string") {
      return payload.detail
    }

    if (status) {
      return `요청 실패 (HTTP ${status})`
    }
  }

  if (error instanceof Error) {
    return error.message
  }
  return "요청 실패"
}

function onUpdateStyles(styles: Style[]) {
  selectedStyles.value = styles
}

async function onGenerate(input: { prompt: string; landingUrl: string | null }) {
  if (loadingCopy.value || loadingLanding.value || loadingUpload.value) {
    return
  }

  const prompt = input.prompt.trim()
  const landingUrl = input.landingUrl?.trim() || null
  if (!prompt) {
    return
  }

  errorMessage.value = ""
  loadingCopy.value = true
  const landingTag = landingUrl ? ` / landing_url=${landingUrl}` : ""
  addTurn("user", `생성 요청: prompt='${prompt.slice(0, 60)}...' / styles=${selectedStyles.value.join(",")}${landingTag}`)

  try {
    const payload: CopyLiteRequest = {
      prompt,
      styles: [...selectedStyles.value],
      landing_url: landingUrl,
      web_search_mode: false,
      use_rag: true,
      top_k: 5,
      rag_document_ids: currentRagDocumentIds.value.length > 0 ? [...currentRagDocumentIds.value] : undefined,
    }

    if (currentRagDocumentIds.value.length > 0) {
      addTurn("assistant", `현재 업로드된 ${currentRagDocumentIds.value.length}개 문서 범위로 RAG 검색을 제한합니다.`)
    }

    const response = await generateCopy(payload)
    result.value = response.result
    generationRound.value += 1
    lastGenerationContext.value = response.normalized_request
    addTurn("assistant", response.assistant_message)
    if (response.assumptions.length > 0) {
      addTurn("assistant", `assumptions: ${response.assumptions.join(" | ")}`)
    }
    addTurn(
      "assistant",
      `자동 완성된 입력: objective=${response.normalized_request.objective}, channel=${response.normalized_request.channel}, language=${response.normalized_request.language}`
    )
    addTurn("assistant", `버전 v${generationRound.value} 생성`)
  } catch (error) {
    errorMessage.value = toError(error)
    addTurn("assistant", `간편 생성 에러: ${errorMessage.value}`)
  } finally {
    loadingCopy.value = false
  }
}

function buildRefinementPrompt(current: CopyGenerateResponse, feedback: string): string {
  const body = current.body.length > 600 ? `${current.body.slice(0, 600)}...` : current.body
  return [
    "아래 기존 카피를 바탕으로 피드백을 우선 반영해 개선해줘.",
    "구조(head/body/cta/slogan/sns/description)는 유지하고 문장 밀도와 설득력을 올려줘.",
    "",
    `[기존 head]\n${current.head}`,
    `[기존 body]\n${body}`,
    `[기존 cta]\n${current.cta}`,
    `[기존 slogan]\n${current.slogan}`,
    `[기존 sns]\n${current.sns}`,
    `[기존 description]\n${current.description}`,
    "",
    `[사용자 피드백]\n${feedback}`,
  ].join("\n")
}

async function onRefine(feedback: string) {
  if (loadingCopy.value || loadingLanding.value || loadingUpload.value) {
    return
  }
  if (!result.value || !lastGenerationContext.value) {
    addTurn("assistant", "먼저 카피를 한 번 생성한 뒤 피드백 개선을 진행해주세요.")
    return
  }

  loadingCopy.value = true
  errorMessage.value = ""
  addTurn("user", `개선 요청: ${feedback}`)

  try {
    const context = lastGenerationContext.value
    const payload: CopyLiteRequest = {
      prompt: buildRefinementPrompt(result.value, feedback),
      styles: context.styles as Style[],
      base_request: context,
      web_search_mode: context.web_search_mode,
      use_rag: context.use_rag,
      top_k: context.top_k,
      rag_document_ids:
        currentRagDocumentIds.value.length > 0
          ? [...currentRagDocumentIds.value]
          : context.rag_document_ids || undefined,
    }

    const response = await generateCopy(payload)
    result.value = response.result
    generationRound.value += 1
    lastGenerationContext.value = response.normalized_request

    addTurn("assistant", `피드백을 반영해 개선 카피를 생성했습니다. (v${generationRound.value})`)
    if (response.assumptions.length > 0) {
      addTurn("assistant", `assumptions: ${response.assumptions.join(" | ")}`)
    }
  } catch (error) {
    errorMessage.value = toError(error)
    addTurn("assistant", `개선 생성 에러: ${errorMessage.value}`)
  } finally {
    loadingCopy.value = false
  }
}

async function onAnalyze(payload: LandingAnalyzeRequest) {
  if (loadingCopy.value || loadingLanding.value || loadingUpload.value) {
    return
  }

  errorMessage.value = ""
  loadingLanding.value = true

  if (payload.url) {
    addTurn("user", `랜딩 분석 요청(URL): ${payload.url}`)
  } else {
    addTurn("user", `랜딩 분석 요청(Query): ${payload.query || "(empty)"}`)
  }

  try {
    const response = await webAgentService.analyze(payload)
    landing.value = response
    addTurn("assistant", `랜딩 분석 완료: h1=${response.h1.length}, h2=${response.h2.length}, cta=${response.cta_buttons.length}`)
  } catch (error) {
    errorMessage.value = toError(error)
    addTurn("assistant", `랜딩 분석 에러: ${errorMessage.value}`)
  } finally {
    loadingLanding.value = false
  }
}

async function onUploadFiles(files: File[]) {
  if (loadingCopy.value || loadingLanding.value || loadingUpload.value || files.length === 0) {
    return
  }

  errorMessage.value = ""
  uploadStatus.value = null
  loadingUpload.value = true
  addTurn("user", `자료 업로드 요청: ${files.map((item) => item.name).join(", ")}`)

  try {
    const upload = await uploadSourceFiles(files)
    addTurn("assistant", `업로드 완료: 성공 ${upload.success_count}/${upload.total_files}, 실패 ${upload.failed_count}`)

    const uploadDetails: string[] = [
      `업로드: 성공 ${upload.success_count}/${upload.total_files}, 실패 ${upload.failed_count}`,
    ]

    const successRows = upload.files.filter((item) => item.success)
    if (successRows.length > 0) {
      const successText = successRows
        .slice(0, 5)
        .map((item) => {
          const engine = (item.conversion_engine || "unknown").trim()
          return `${item.file_name}(${engine}, ${item.text_length}자)`
        })
        .join(", ")
      addTurn("assistant", `텍스트 인식 성공 파일: ${successText}`)
      uploadDetails.push(`인식 성공 파일: ${successText}`)
    }

    const successfulDocumentIds = upload.files
      .filter((item) => item.success && item.document_id)
      .map((item) => String(item.document_id))

    currentRagDocumentIds.value = successfulDocumentIds

    const failedRows = upload.files.filter((item) => !item.success)
    if (failedRows.length > 0) {
      const failedText = failedRows
        .slice(0, 5)
        .map((item) => {
          const code = item.error_code || "ERROR"
          const reason = (item.error_message || "원인 미상").trim()
          return `${item.file_name}(${code}: ${reason})`
        })
        .join(", ")
      addTurn("assistant", `업로드 실패 파일: ${failedText}`)
      uploadDetails.push(`실패 파일: ${failedText}`)
    }

    if (successfulDocumentIds.length === 0) {
      if (upload.success_count > 0) {
        addTurn("assistant", "인덱싱할 문서 ID가 없어 인덱싱은 건너뜁니다.")
        uploadDetails.push("인덱싱: 문서 ID가 없어 건너뜀")
        uploadStatus.value = {
          level: upload.failed_count > 0 ? "warning" : "success",
          title: upload.failed_count > 0 ? "자료 업로드 완료 (일부 실패)" : "자료 업로드 완료",
          details: uploadDetails,
        }
      } else {
        addTurn("assistant", "업로드 성공 문서가 없어 인덱싱을 진행하지 않았습니다.")
        uploadStatus.value = {
          level: "error",
          title: "자료 업로드 실패",
          details: uploadDetails,
        }
      }
      return
    }

    const indexed = await indexRagDocuments(successfulDocumentIds)
    addTurn("assistant", `인덱싱 완료: 문서 ${indexed.indexed_documents}개, 청크 ${indexed.indexed_chunks}개`)
    uploadDetails.push(`인덱싱: 문서 ${indexed.indexed_documents}개, 청크 ${indexed.indexed_chunks}개`)
    if (indexed.missing_document_ids.length > 0) {
      addTurn("assistant", `누락 document_id: ${indexed.missing_document_ids.join(", ")}`)
      uploadDetails.push(`누락 document_id: ${indexed.missing_document_ids.join(", ")}`)
    }

    uploadStatus.value = {
      level: upload.failed_count > 0 || indexed.missing_document_ids.length > 0 ? "warning" : "success",
      title:
        upload.failed_count > 0 || indexed.missing_document_ids.length > 0
          ? "자료 업로드/인덱싱 완료 (일부 실패)"
          : "자료 업로드/인덱싱 완료",
      details: uploadDetails,
    }
  } catch (error) {
    errorMessage.value = toError(error)
    uploadStatus.value = {
      level: "error",
      title: "자료 업로드 실패",
      details: [errorMessage.value],
    }
    addTurn("assistant", `파일 업로드/인덱싱 에러: ${errorMessage.value}`)
  } finally {
    loadingUpload.value = false
  }
}

async function onResetGeneration() {
  if (loadingCopy.value || loadingLanding.value || loadingUpload.value) {
    return
  }

  loadingUpload.value = true
  errorMessage.value = ""

  try {
    const reset = await resetRagIndex()
    uploadStatus.value = {
      level: "success",
      title: "제너레이션/자료 인덱스 초기화 완료",
      details: [
        `정리된 문서: ${reset.cleared_documents}개`,
        `정리된 벡터: ${reset.cleared_vectors}개`,
        `백엔드: ${reset.backend}`,
      ],
    }
  } catch (error) {
    errorMessage.value = toError(error)
    uploadStatus.value = {
      level: "error",
      title: "자료 인덱스 초기화 실패",
      details: [errorMessage.value],
    }
  } finally {
    loadingUpload.value = false
  }

    result.value = null
    landing.value = null
    turns.value = []
    generationRound.value = 0
    lastGenerationContext.value = null
    currentRagDocumentIds.value = []
}
</script>

<template>
  <main class="page">
    <section class="hero">
      <h1>Copyjoe</h1>
    </section>

    <section class="layout">
      <aside class="sidebar-panel">
        <PromptSection
          :loading-copy="loadingCopy"
          :loading-landing="loadingLanding"
          :loading-upload="loadingUpload"
          :upload-status="uploadStatus"
          :styles="selectedStyles"
          @update:styles="onUpdateStyles"
          @analyze="onAnalyze"
          @upload-files="onUploadFiles"
        />
      </aside>
      <section class="main-panel">
        <GenerationSection
          :result="result"
          :landing="landing"
          :turns="turns"
          :loading-copy="loadingCopy"
          :loading-landing="loadingLanding"
          :loading-upload="loadingUpload"
          :error-message="errorMessage"
          :styles="selectedStyles"
          @generate="onGenerate"
          @refine="onRefine"
          @reset-generation="onResetGeneration"
        />
      </section>
    </section>
  </main>
</template>
