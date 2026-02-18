<script setup lang="ts">
import { computed, reactive, ref } from "vue"

import type { LandingAnalyzeRequest, Style } from "../models-service/types"
import LoadingSpinner from "../components/LoadingSpinner.vue"

const props = defineProps<{
  styles: Style[]
  loadingCopy: boolean
  loadingLanding: boolean
  loadingUpload: boolean
  uploadStatus: {
    level: "success" | "warning" | "error"
    title: string
    details: string[]
  } | null
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
})

const selectedStylesText = computed(() => {
  if (props.styles.length === 0) {
    return defaultStyles.join(", ")
  }
  return props.styles.join(", ")
})

const canAnalyzeLanding = computed(() => landingInput.url.trim().length > 0)

const uploadStatusBorderColor = computed(() => {
  if (!props.uploadStatus) {
    return "#94a8ff"
  }
  if (props.uploadStatus.level === "error") {
    return "#f05b5b"
  }
  if (props.uploadStatus.level === "warning") {
    return "#ff9c67"
  }
  return "#2cb67d"
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
  if (isBusy.value || !canAnalyzeLanding.value) {
    return
  }

  const url = landingInput.url.trim()
  emit("analyze", {
    url: url || null,
    query: null,
    max_results: 5,
  })
}
</script>

<template>
  <div class="card">
    <h2>입력 설정</h2>

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

    <hr style="margin: 14px 0; border: 0; border-top: 1px solid #e6edeb" />

    <h3 style="margin: 0 0 8px">자료 업로드</h3>
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
    <LoadingSpinner v-if="loadingUpload" />

    <div v-if="uploadStatus" class="result-block" :style="{ marginTop: '10px', borderLeftColor: uploadStatusBorderColor }">
      <strong>{{ uploadStatus.title }}</strong>
      <ul v-if="uploadStatus.details.length > 0" style="margin: 8px 0 0; padding-left: 18px">
        <li v-for="(detail, index) in uploadStatus.details" :key="`upload-status-${index}`">{{ detail }}</li>
      </ul>
    </div>

    <hr style="margin: 14px 0; border: 0; border-top: 1px solid #e6edeb" />

    <h3 style="margin: 0 0 8px">랜딩 분석</h3>
    <label>
      landing_url
      <input v-model="landingInput.url" :disabled="isBusy" placeholder="https://example.com" />
    </label>

    <button class="secondary" style="margin-top: 10px" :disabled="isBusy || !canAnalyzeLanding" @click="onAnalyze">랜딩 분석 실행</button>
    <LoadingSpinner v-if="loadingLanding" />
  </div>
</template>
