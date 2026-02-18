<script setup lang="ts">
import { computed, ref } from "vue"

import type { CopyGenerateResponse, LandingAnalyzeResponse } from "../models-service/types"
import GenerateResult from "../components/GenerateResult.vue"
import LoadingSpinner from "../components/LoadingSpinner.vue"

const props = defineProps<{
  result: CopyGenerateResponse | null
  landing: LandingAnalyzeResponse | null
  turns: Array<{ role: "user" | "assistant"; text: string }>
  loadingCopy: boolean
  loadingLanding: boolean
  loadingUpload: boolean
  errorMessage: string
}>()

const emit = defineEmits<{
  refine: [feedback: string]
  resetGeneration: []
}>()

const feedbackInput = ref("")
const hasGenerationData = computed(
  () => !!props.result || !!props.landing || props.turns.length > 0 || !!props.errorMessage
)

const landingInsights = computed(() => {
  if (!props.landing) {
    return [] as string[]
  }

  const rows: string[] = []
  const landing = props.landing

  if (landing.h1.length === 0) {
    rows.push("메인 가치제안(h1)이 없어 첫 화면 메시지가 약할 가능성이 큽니다.")
  } else {
    rows.push(`핵심 메시지(h1): '${landing.h1[0]}'`)
  }

  if (landing.cta_buttons.length <= 1) {
    rows.push("CTA 개수가 적어 행동 유도 실험 여지가 큽니다. 주요 CTA를 2개 이상 비교해보세요.")
  } else {
    rows.push(`CTA 버튼/링크가 ${landing.cta_buttons.length}개로 추출되어 전환 동선 실험 포인트가 충분합니다.`)
  }

  if (landing.h2.length < 3) {
    rows.push("섹션 구조(h2)가 단순합니다. 문제-해결-근거-CTA 구조로 확장하면 설득 흐름이 좋아집니다.")
  } else {
    rows.push(`섹션 헤드라인(h2) ${landing.h2.length}개를 기반으로 메시지 구조를 파악할 수 있습니다.`)
  }

  if (landing.body.length < 500) {
    rows.push("본문 정보량이 낮습니다. 기능 근거/사용 사례/리스크 완화 문장을 보강하는 편이 좋습니다.")
  } else {
    rows.push("본문 텍스트가 충분해 주요 설득 포인트와 약점을 비교 분석할 수 있습니다.")
  }

  return rows
})

function onSubmitRefine() {
  const feedback = feedbackInput.value.trim()
  if (!feedback || !props.result || props.loadingCopy || props.loadingLanding || props.loadingUpload) {
    return
  }
  emit("refine", feedback)
  feedbackInput.value = ""
}

function onResetGeneration() {
  if (props.loadingCopy || props.loadingLanding || props.loadingUpload || !hasGenerationData.value) {
    return
  }
  feedbackInput.value = ""
  emit("resetGeneration")
}
</script>

<template>
  <div class="card">
    <h2>GenerationSection.vue</h2>
    <p class="muted">대화형 흐름과 생성 결과를 함께 보여줍니다.</p>

    <div style="display: flex; justify-content: flex-end; margin-bottom: 10px">
      <button :disabled="loadingCopy || loadingLanding || loadingUpload || !hasGenerationData" @click="onResetGeneration">제너레이션 초기화</button>
    </div>

    <h3 style="margin-bottom: 8px">대화형 로그</h3>
    <div v-if="turns.length === 0" class="muted">아직 대화가 없습니다.</div>
    <div v-for="(turn, index) in turns" :key="`${index}-${turn.role}`" class="turn" :class="turn.role">
      <strong>{{ turn.role === "user" ? "USER" : "ASSISTANT" }}</strong>
      <div style="margin-top: 4px">{{ turn.text }}</div>
    </div>

    <LoadingSpinner v-if="loadingCopy || loadingLanding || loadingUpload" />
    <p v-if="errorMessage" class="muted">에러: {{ errorMessage }}</p>

    <div v-if="result" class="result-block">
      <h3 style="margin-top: 0">대화 기반 개선</h3>
      <p class="muted" style="margin-top: 4px">
        현재 결과를 기준으로 피드백을 주면 다음 버전 카피를 다시 생성합니다.
      </p>
      <label>
        개선 피드백
        <textarea
          v-model="feedbackInput"
          rows="2"
          placeholder="예: CTA를 더 긴급하게, 본문은 신뢰 근거를 숫자로 제시해줘"
          :disabled="loadingCopy || loadingLanding || loadingUpload"
          @keyup.enter.exact.prevent="onSubmitRefine"
        />
      </label>
      <button class="primary" style="margin-top: 8px" :disabled="loadingCopy || loadingLanding || loadingUpload || !feedbackInput.trim()" @click="onSubmitRefine">
        피드백 반영 재생성
      </button>
    </div>

    <template v-if="result">
      <h3>GenerateResult.vue</h3>
      <GenerateResult :result="result" />
    </template>

    <template v-if="landing">
      <h3>랜딩 분석 결과</h3>
      <div class="result-block">
        <p><strong>url:</strong> {{ landing.url }}</p>
        <p><strong>title:</strong> {{ landing.title }}</p>
        <p><strong>from_tavily:</strong> {{ landing.from_tavily }}</p>
        <p><strong>h1:</strong> {{ landing.h1.join(" | ") }}</p>
        <p><strong>h2 count:</strong> {{ landing.h2.length }}</p>
        <p><strong>cta count:</strong> {{ landing.cta_buttons.length }}</p>
        <div class="mono">{{ landing.body }}</div>
      </div>
      <div class="result-block">
        <h4 style="margin-top: 0">이 랜딩에서 알 수 있는 것</h4>
        <ul>
          <li v-for="(item, index) in landingInsights" :key="`insight-${index}`">{{ item }}</li>
        </ul>
      </div>
    </template>
  </div>
</template>
