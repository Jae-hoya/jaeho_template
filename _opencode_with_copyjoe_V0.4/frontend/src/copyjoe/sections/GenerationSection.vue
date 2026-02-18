<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue"

import type { CopyGenerateResponse, LandingAnalyzeResponse, Style } from "../models-service/types"
import GenerateResult from "../components/GenerateResult.vue"
import LoadingSpinner from "../components/LoadingSpinner.vue"

type GenerateInput = {
  prompt: string
  landingUrl: string | null
}

const props = defineProps<{
  result: CopyGenerateResponse | null
  landing: LandingAnalyzeResponse | null
  turns: Array<{ role: "user" | "assistant"; text: string }>
  styles: Style[]
  loadingCopy: boolean
  loadingLanding: boolean
  loadingUpload: boolean
  errorMessage: string
}>()

const emit = defineEmits<{
  generate: [payload: GenerateInput]
  refine: [feedback: string]
  resetGeneration: []
}>()

const generationInput = ref("")
const feedbackInput = ref("")
const isLogExpanded = ref(true)
const logViewportRef = ref<HTMLDivElement | null>(null)
const hasGenerationData = computed(
  () => !!props.result || !!props.landing || props.turns.length > 0 || !!props.errorMessage
)
const selectedStylesText = computed(() => props.styles.join(", "))
const visibleTurns = computed(() => props.turns)

watch(
  () => [props.turns.length, isLogExpanded.value] as const,
  async ([, expanded]) => {
    if (!expanded) {
      return
    }
    await nextTick()
    const viewport = logViewportRef.value
    if (!viewport) {
      return
    }
    viewport.scrollTop = viewport.scrollHeight
  },
  { immediate: true }
)

const practicalQuestionExamples = [
  "메타 광고 CTR이 떨어졌어요. 데모 신청을 늘릴 신뢰형 카피가 필요합니다.",
  "상세페이지 장바구니 전환이 약해요. 가격 저항을 낮추는 카피를 만들고 싶어요.",
  "이메일 캠페인 무료체험 클릭률이 낮아요. 2B SaaS 톤으로 짧고 강한 문구가 필요합니다.",
]

function joinOrDefault(items: string[], maxCount: number): string {
  const picked = items.slice(0, maxCount)
  return picked.length > 0 ? picked.join(" | ") : "(없음)"
}

function buildLandingStoryboardPrompt(landing: LandingAnalyzeResponse): string {
  return [
    "아래 랜딩페이지를 기반으로 전환형 광고 콘티를 작성해줘.",
    "- storyboard_outline을 가장 구체적으로 작성하고 장면별 메시지/행동 유도를 포함",
    "- 랜딩의 핵심 가치제안(h1/h2/cta)과 흐름을 유지",
    "- 결과 구조(head/body/cta/slogan/sns/description)는 유지",
    "",
    `[랜딩 title]\n${landing.title || "(없음)"}`,
    `[랜딩 h1]\n${joinOrDefault(landing.h1, 6)}`,
    `[랜딩 h2]\n${joinOrDefault(landing.h2, 10)}`,
    `[랜딩 cta]\n${joinOrDefault(landing.cta_buttons, 12)}`,
  ].join("\n")
}

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

function onSubmitGenerate() {
  const prompt = generationInput.value.trim()
  if (!prompt || props.loadingCopy || props.loadingLanding || props.loadingUpload) {
    return
  }

  emit("generate", {
    prompt,
    landingUrl: props.landing?.url || null,
  })
  generationInput.value = ""
}

function applyPracticalExample(example: string) {
  if (props.loadingCopy || props.loadingLanding || props.loadingUpload) {
    return
  }
  generationInput.value = example
}

function clearGenerationInput() {
  if (props.loadingCopy || props.loadingLanding || props.loadingUpload) {
    return
  }
  generationInput.value = ""
}

function onGenerateStoryboardFromLanding() {
  if (!props.landing || props.loadingCopy || props.loadingLanding || props.loadingUpload) {
    return
  }

  emit("generate", {
    prompt: buildLandingStoryboardPrompt(props.landing),
    landingUrl: props.landing.url,
  })
}

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
  generationInput.value = ""
  feedbackInput.value = ""
  emit("resetGeneration")
}

function toggleLogPanel() {
  isLogExpanded.value = !isLogExpanded.value
}
</script>

<template>
  <div class="card">
    <h2>카피 생성</h2>

    <div style="display: flex; justify-content: flex-end; margin-bottom: 10px">
      <button :disabled="loadingCopy || loadingLanding || loadingUpload || !hasGenerationData" @click="onResetGeneration">제너레이션 초기화</button>
    </div>

    <div class="result-block">
      <h3 style="margin-top: 0">대화형 입력</h3>
      <p class="muted" style="margin-top: 4px">선택 스타일: {{ selectedStylesText }}</p>

      <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 8px">
        <button
          v-for="(example, index) in practicalQuestionExamples"
          :key="`example-${index}`"
          style="text-align: left"
          :disabled="loadingCopy || loadingLanding || loadingUpload"
          @click="applyPracticalExample(example)"
        >
          {{ example }}
        </button>
      </div>

      <label style="margin-top: 10px">
        대화형 브리프
        <textarea
          v-model="generationInput"
          rows="4"
          :disabled="loadingCopy || loadingLanding || loadingUpload"
          placeholder="채널, 문제 상황, 목표 행동, 원하는 톤을 자연어로 적어주세요"
          @keyup.enter.exact.prevent="onSubmitGenerate"
        />
      </label>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="primary" :disabled="loadingCopy || loadingLanding || loadingUpload || !generationInput.trim()" @click="onSubmitGenerate">카피 생성</button>
        <button :disabled="loadingCopy || loadingLanding || loadingUpload || !generationInput.trim()" @click="clearGenerationInput">입력 초기화</button>
      </div>
    </div>

    <div class="result-block" style="margin-top: 12px">
      <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px">
        <h3 style="margin: 0">대화형 로그</h3>
        <button :disabled="turns.length === 0" @click="toggleLogPanel">{{ isLogExpanded ? "접기" : "펼치기" }}</button>
      </div>
      <p class="muted" style="margin: 8px 0 0">전체 로그를 표시합니다.</p>

      <div
        v-if="isLogExpanded"
        ref="logViewportRef"
        style="max-height: 300px; overflow-y: auto; margin-top: 10px; padding: 10px; border: 1px solid #d9e3f8; border-radius: 12px; background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%)"
      >
        <div v-if="visibleTurns.length === 0" class="muted">아직 대화가 없습니다.</div>
        <div v-for="(turn, index) in visibleTurns" :key="`${index}-${turn.role}`" class="turn" :class="turn.role">
          <strong>{{ turn.role === "user" ? "USER" : "ASSISTANT" }}</strong>
          <div style="margin-top: 4px">{{ turn.text }}</div>
        </div>
      </div>

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
      <h3>생성 결과</h3>
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
        <button class="primary" style="margin-bottom: 10px" :disabled="loadingCopy || loadingLanding || loadingUpload" @click="onGenerateStoryboardFromLanding">
          이 랜딩으로 콘티 작성
        </button>
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
