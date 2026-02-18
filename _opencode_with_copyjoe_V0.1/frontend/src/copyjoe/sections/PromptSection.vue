<script setup lang="ts">
import { computed, reactive, ref } from "vue"

import type { LandingAnalyzeRequest, Style } from "../models-service/types"

const props = defineProps<{
  styles: Style[]
  loadingCopy: boolean
  loadingLanding: boolean
  loadingUpload: boolean
}>()

const emit = defineEmits<{
  "update:styles": [styles: Style[]]
  analyze: [payload: LandingAnalyzeRequest]
  uploadFiles: [files: File[]]
}>()

const isBusy = computed(() => props.loadingCopy || props.loadingLanding || props.loadingUpload)

const styleOptions: Array<{ value: Style; hint: string }> = [
  { value: "head", hint: "첫 인지용 헤드라인" },
  { value: "body", hint: "핵심 설득 본문" },
  { value: "cta", hint: "행동 유도 문구" },
  { value: "slogan", hint: "짧은 반복 슬로건" },
  { value: "sns", hint: "SNS 단문 카피" },
  { value: "description", hint: "설명/요약 카피" },
]

const defaultStyles: Style[] = styleOptions.map((item) => item.value)

const uploadInputRef = ref<HTMLInputElement | null>(null)
const selectedUploadFiles = ref<File[]>([])

const landingInput = reactive({
  url: "",
  query: "copywriting saas landing page",
})

const selectedStylesText = computed(() => {
  if (props.styles.length === 0) {
    return defaultStyles.join(", ")
  }
  return props.styles.join(", ")
})

function onUploadFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files ? Array.from(target.files) : []
  selectedUploadFiles.value = files
}

function clearUploadSelection() {
  selectedUploadFiles.value = []
  if (uploadInputRef.value) {
    uploadInputRef.value.value = ""
  }
}

function submitUploadFiles() {
  if (isBusy.value || selectedUploadFiles.value.length === 0) {
    return
  }
  emit("uploadFiles", [...selectedUploadFiles.value])
  clearUploadSelection()
}

function isStyleSelected(style: Style): boolean {
  return props.styles.includes(style)
}

function toggleStyle(style: Style) {
  if (isBusy.value) {
    return
  }

  const activeStyles = props.styles.length > 0 ? props.styles : defaultStyles

  if (isStyleSelected(style)) {
    if (activeStyles.length === 1) {
      return
    }
    emit(
      "update:styles",
      defaultStyles.filter((item) => activeStyles.includes(item) && item !== style)
    )
    return
  }

  const next = [...activeStyles, style]
  emit(
    "update:styles",
    defaultStyles.filter((item) => next.includes(item))
  )
}

function onAnalyze() {
  if (isBusy.value) {
    return
  }

  const url = landingInput.url.trim()
  const query = landingInput.query.trim()
  emit("analyze", {
    url: url || null,
    query: url ? null : query || null,
    max_results: 5,
  })
}
</script>

<template>
  <div class="card">
    <h2>PromptSection.vue</h2>
    <p class="muted">스타일만 고르고, 나머지는 대화형 브리프로 처리합니다.</p>

    <div class="result-block" style="margin-top: 10px">
      <strong>출력 스타일 선택</strong>
      <p class="muted" style="margin: 6px 0 0">필요한 스타일만 남기면 해당 항목 중심으로 결과가 생성됩니다.</p>
      <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px">
        <button
          v-for="item in styleOptions"
          :key="`style-${item.value}`"
          :class="isStyleSelected(item.value) ? 'primary' : ''"
          :disabled="isBusy"
          @click="toggleStyle(item.value)"
        >
          {{ item.value }}
        </button>
      </div>
      <div class="muted" style="margin: 8px 0 0; display: inline-flex; align-items: center; gap: 6px">
        <span>선택 스타일: {{ selectedStylesText }}</span>
        <span class="tooltip-wrap">
          <span class="help-icon" tabindex="0" aria-label="스타일 설명">?</span>
          <span class="tooltip-content">
            <span v-for="item in styleOptions" :key="`style-hint-${item.value}`" class="tooltip-line">
              {{ item.value }}: {{ item.hint }}
            </span>
          </span>
        </span>
      </div>
    </div>

    <p class="muted" style="margin: 10px 0 0">
      대화 입력은 오른쪽 Generation 영역에서 진행됩니다. objective/channel/language는 프롬프트 문맥으로 자동 추론됩니다.
    </p>

    <hr style="margin: 14px 0; border: 0; border-top: 1px solid #e6edeb" />

    <h3 style="margin: 0 0 8px">RAG 자료 업로드</h3>
    <p class="muted" style="margin: 0 0 8px">문서 업로드 후 자동 인덱싱되어 카피 생성 시 근거로 활용됩니다.</p>
    <label>
      파일 선택 (pdf/doc/docx/txt/xls/xlsx/ppt/pptx/png/jpg)
      <input
        ref="uploadInputRef"
        type="file"
        multiple
        accept=".pdf,.doc,.docx,.txt,.xls,.xlsx,.ppt,.pptx,.png,.jpg,.jpeg"
        :disabled="isBusy"
        @change="onUploadFileChange"
      />
    </label>
    <p v-if="selectedUploadFiles.length > 0" class="muted" style="margin: 6px 0 0">
      선택됨: {{ selectedUploadFiles.map((item) => item.name).join(", ") }}
    </p>
    <div style="display: flex; gap: 8px; margin-top: 10px">
      <button class="primary" :disabled="isBusy || selectedUploadFiles.length === 0" @click="submitUploadFiles">업로드 + 인덱싱</button>
      <button :disabled="isBusy || selectedUploadFiles.length === 0" @click="clearUploadSelection">선택 초기화</button>
    </div>

    <hr style="margin: 14px 0; border: 0; border-top: 1px solid #e6edeb" />

    <h3 style="margin: 0 0 8px">랜딩 분석</h3>
    <label>
      landing_url
      <input v-model="landingInput.url" :disabled="isBusy" placeholder="https://example.com" />
    </label>
    <label>
      landing_query
      <input v-model="landingInput.query" :disabled="isBusy" placeholder="url 없을 때 Tavily 검색 쿼리" />
    </label>

    <button class="secondary" style="margin-top: 10px" :disabled="isBusy" @click="onAnalyze">랜딩 분석 실행</button>
  </div>
</template>
