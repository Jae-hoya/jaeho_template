<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from "vue"

import PromptOption from "../components/PromptOption.vue"
import type {
  CopyGenerateRequest,
  CopyLiteRequest,
  LandingAnalyzeRequest,
  Objective,
  Style,
} from "../models-service/types"

const props = defineProps<{
  loadingCopy: boolean
  loadingLanding: boolean
  loadingUpload: boolean
}>()

const emit = defineEmits<{
  generate: [payload: CopyGenerateRequest]
  generateLite: [payload: CopyLiteRequest]
  analyze: [payload: LandingAnalyzeRequest]
  uploadFiles: [files: File[]]
}>()

const isBusy = computed(() => props.loadingCopy || props.loadingLanding || props.loadingUpload)
const mode = ref<"guided" | "advanced">("guided")

const advanced = reactive({
  product_name: "Copyjoe",
  target_audience: "퍼포먼스 마케터",
  pain_point: "광고 성과는 압박되는데, A/B 테스트용 카피를 빠르게 대량 생성하지 못해 집행 최적화가 늦어진다.",
  differentiator: "LangGraph 오케스트레이션으로 RAG 문서 근거와 Tavily 웹 근거를 결합해, 실행 가능한 퍼포먼스 카피를 일관된 포맷으로 빠르게 생성한다.",
  tone: "신뢰형",
  objective: "click",
  channel: "메타 광고 랜딩",
  language: "ko",
  top_k: 5,
  web_search_mode: false,
  use_rag: true,
  styles: {
    head: true,
    body: true,
    cta: true,
    slogan: true,
    sns: true,
    description: true,
  },
  landing_url: "",
  landing_query: "copywriting saas landing page",
})

const guided = reactive({
  prompt:
    "클릭률이 떨어져서 신뢰형 카피가 필요합니다. 빠르게 A/B 테스트 가능한 문구를 만들고 싶어요.",
  styles: ["head", "body", "cta", "slogan", "sns", "description"] as Style[],
  objective: "click" as Objective,
  channel: "상세페이지",
  language: "ko",
})

type GuidedStep = "prompt" | "styles" | "objective" | "channel" | "ready"
const guidedStep = ref<GuidedStep>("prompt")
const guidedInput = ref("")
const guidedLogRef = ref<HTMLDivElement | null>(null)
const guidedMessages = ref<Array<{ role: "assistant" | "user"; text: string }>>([
  {
    role: "assistant",
    text: "안녕하세요. 실무 질문 형태로 브리프를 주세요. (채널 + 지표 문제 + 원하는 행동)",
  },
  {
    role: "assistant",
    text: "예: '메타 광고 CTR이 0.9%로 떨어졌어요. 데모 신청 늘릴 카피 필요'",
  },
  {
    role: "assistant",
    text: "결과에는 head/body/cta/slogan/sns/description + storyboard_outline + rationale가 포함됩니다.",
  },
  {
    role: "assistant",
    text: "출력 언어는 아래 버튼에서 선택할 수 있어요. (예: ko, en, ja)",
  },
])

const practicalQuestionExamples = [
  "메타 광고 CTR이 0.9%로 떨어졌어요. 퍼포먼스 마케터 대상 데모 신청을 늘릴 카피가 필요해요.",
  "상세페이지 장바구니 전환이 약해요. 가격 저항을 낮추는 구매 유도 카피를 만들고 싶어요.",
  "이메일 캠페인 무료체험 클릭률이 낮아요. HR SaaS 톤으로 클릭 유도 카피가 필요합니다.",
]

const guidedLanguageOptions = [
  { label: "ko", value: "ko" },
  { label: "en", value: "en" },
  { label: "ja", value: "ja" },
  { label: "zh-CN", value: "zh-CN" },
  { label: "zh-TW", value: "zh-TW" },
]

const uploadInputRef = ref<HTMLInputElement | null>(null)
const selectedUploadFiles = ref<File[]>([])

const objectiveOptions = [
  { label: "brand_memory", value: "brand_memory" },
  { label: "click", value: "click" },
  { label: "add_to_cart", value: "add_to_cart" },
  { label: "consultation", value: "consultation" },
]

const toneOptions = [
  { label: "신뢰형", value: "신뢰형" },
  { label: "도전형", value: "도전형" },
  { label: "친근형", value: "친근형" },
]

const languageOptions = [
  { label: "ko (한국어)", value: "ko" },
  { label: "en (English)", value: "en" },
  { label: "ja (Japanese)", value: "ja" },
  { label: "zh-CN (简体中文)", value: "zh-CN" },
  { label: "zh-TW (繁體中文)", value: "zh-TW" },
  { label: "es (Español)", value: "es" },
  { label: "fr (Français)", value: "fr" },
  { label: "de (Deutsch)", value: "de" },
  { label: "pt-BR (Português)", value: "pt-BR" },
  { label: "vi (Tiếng Việt)", value: "vi" },
  { label: "id (Bahasa Indonesia)", value: "id" },
  { label: "th (ไทย)", value: "th" },
]

const objectiveGuide = {
  brand_memory: "브랜드 인지/기억 강화",
  click: "클릭 유도 (CTR 중심)",
  add_to_cart: "장바구니 추가 유도",
  consultation: "상담/문의 유도",
} as const

const guidedPlaceholder = computed(() => {
  if (guidedStep.value === "prompt") {
    return "예: 메타 광고 CTR이 0.9%로 하락. 상담 신청 전환을 올릴 카피 필요"
  }
  if (guidedStep.value === "styles") {
    return "예: all 또는 head, body, cta, slogan, sns, description"
  }
  if (guidedStep.value === "objective") {
    return "예: CTR 목표면 click, 장바구니면 add_to_cart, 상담이면 consultation"
  }
  if (guidedStep.value === "channel") {
    return "예: 메타 광고 랜딩 / 상세페이지 / 카카오 친구톡 랜딩"
  }
  return "다시 시작하려면 '다시' 입력"
})

function applyPracticalExample(example: string) {
  if (isBusy.value || guidedStep.value != "prompt") {
    return
  }
  guidedInput.value = example
}

function setGuidedLanguage(code: string) {
  if (isBusy.value) {
    return
  }
  guided.language = code
}

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

function selectedAdvancedStyles(): Style[] {
  return (Object.keys(advanced.styles) as Style[]).filter((key) => advanced.styles[key])
}

function scrollGuidedToBottom() {
  void nextTick(() => {
    if (!guidedLogRef.value) {
      return
    }
    guidedLogRef.value.scrollTop = guidedLogRef.value.scrollHeight
  })
}

watch(
  () => guidedMessages.value.length,
  () => {
    scrollGuidedToBottom()
  }
)

function selectedGuidedStylesText(): string {
  return guided.styles.join(", ")
}

function addAssistant(text: string) {
  guidedMessages.value.push({ role: "assistant", text })
}

function addUser(text: string) {
  guidedMessages.value.push({ role: "user", text })
}

function parseStyles(input: string): Style[] {
  const normalized = input.toLowerCase().replace(/\s+/g, "")
  if (normalized === "all" || normalized === "전체") {
    return ["head", "body", "cta", "slogan", "sns", "description"]
  }

  const tokens = input
    .split(/[,/|]+/)
    .map((item) => item.trim().toLowerCase())
    .filter(Boolean)

  const map: Record<string, Style> = {
    head: "head",
    헤드: "head",
    헤드라인: "head",
    body: "body",
    본문: "body",
    cta: "cta",
    행동유도: "cta",
    slogan: "slogan",
    슬로건: "slogan",
    sns: "sns",
    description: "description",
    설명: "description",
  }

  const picked = tokens
    .map((item) => map[item])
    .filter((item): item is Style => typeof item === "string")

  const deduped = Array.from(new Set(picked))
  if (deduped.length === 0) {
    return ["head", "body", "cta", "slogan", "sns", "description"]
  }
  return deduped
}

function parseObjective(input: string): Objective {
  const text = input.trim().toLowerCase()
  const map: Record<string, Objective> = {
    brand_memory: "brand_memory",
    브랜드인지: "brand_memory",
    브랜드기억: "brand_memory",
    click: "click",
    클릭: "click",
    ctr: "click",
    add_to_cart: "add_to_cart",
    장바구니: "add_to_cart",
    장바구니추가: "add_to_cart",
    consultation: "consultation",
    상담: "consultation",
    문의: "consultation",
  }
  return map[text] || "click"
}

function resetGuidedConversation() {
  guidedStep.value = "prompt"
  guidedInput.value = ""
  guided.styles = ["head", "body", "cta", "slogan", "sns", "description"]
  guided.objective = "click"
  guided.channel = "상세페이지"
  guided.language = "ko"
  guidedMessages.value = [
    {
      role: "assistant",
      text: "좋아요, 다시 시작할게요. 먼저 한 줄 브리프를 주세요.",
    },
    {
      role: "assistant",
      text: "결과에는 slogan/sns/description/storyboard_outline/rationale도 포함됩니다.",
    },
    {
      role: "assistant",
      text: "출력 언어는 아래 버튼에서 선택할 수 있어요.",
    },
  ]
}

function buildGuidedPayload(): CopyLiteRequest {
  return {
    prompt: guided.prompt,
    styles: guided.styles,
    objective: guided.objective,
    channel: guided.channel,
    language: guided.language,
    web_search_mode: false,
    use_rag: true,
    top_k: 5,
  }
}

function onGuidedSend() {
  if (isBusy.value) {
    return
  }

  const text = guidedInput.value.trim()
  if (!text) {
    return
  }

  addUser(text)
  guidedInput.value = ""

  if (guidedStep.value === "ready") {
    if (text === "다시") {
      resetGuidedConversation()
      return
    }
    addAssistant("이미 생성 요청을 보냈어요. 다시 진행하려면 '다시'를 입력해주세요.")
    return
  }

  if (guidedStep.value === "prompt") {
    guided.prompt = text
    guidedStep.value = "styles"
    addAssistant("좋아요. 원하는 copy style을 알려주세요. 예: all 또는 head, body, cta, slogan, sns, description")
    addAssistant("storyboard_outline과 rationale은 항상 함께 생성됩니다.")
    return
  }

  if (guidedStep.value === "styles") {
    guided.styles = parseStyles(text)
    guidedStep.value = "objective"
    addAssistant("좋습니다. 목표(objective)는 무엇인가요? KPI 기준으로 입력하면 됩니다. 예: click")
    addAssistant("옵션: brand_memory / click / add_to_cart / consultation")
    return
  }

  if (guidedStep.value === "objective") {
    guided.objective = parseObjective(text)
    guidedStep.value = "channel"
    addAssistant(`확인했습니다. objective=${guided.objective}. 이제 채널(channel)을 알려주세요. 예: 메타 광고 랜딩`)
    addAssistant(`언어는 아래 버튼에서 고를 수 있어요. 현재 선택: ${guided.language}`)
    return
  }

  if (guidedStep.value === "channel") {
    guided.channel = text === "기본값" ? "상세페이지" : text
    addAssistant(
      `좋아요. 정리하면 style=${selectedGuidedStylesText()}, objective=${guided.objective}, channel=${guided.channel}, language=${guided.language}, top_k=5 입니다.`
    )
    addAssistant("지금 카피 생성을 시작합니다.")
    guidedStep.value = "ready"
    emit("generateLite", buildGuidedPayload())
    return
  }
}

function onGenerateAdvanced() {
  if (isBusy.value) {
    return
  }

  emit("generate", {
    product_name: advanced.product_name,
    target_audience: advanced.target_audience,
    pain_point: advanced.pain_point,
    differentiator: advanced.differentiator,
    tone: advanced.tone,
    objective: advanced.objective as Objective,
    styles: selectedAdvancedStyles(),
    channel: advanced.channel,
    language: advanced.language,
    web_search_mode: advanced.web_search_mode,
    use_rag: advanced.use_rag,
    top_k: Number(advanced.top_k),
  })
}

function onAnalyze() {
  if (isBusy.value) {
    return
  }

  const url = advanced.landing_url.trim()
  const query = advanced.landing_query.trim()
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
    <p class="muted">처리 중에는 새 생성 요청이 잠겨 중복 실행을 막습니다.</p>

    <div style="display: flex; gap: 8px; margin-bottom: 10px">
      <button :class="mode === 'guided' ? 'primary' : ''" :disabled="isBusy" @click="mode = 'guided'">간편 대화형</button>
      <button :class="mode === 'advanced' ? 'primary' : ''" :disabled="isBusy" @click="mode = 'advanced'">상세 입력</button>
    </div>

    <template v-if="mode === 'guided'">
      <div ref="guidedLogRef" class="result-block" style="max-height: 260px; overflow: auto">
        <div v-for="(item, index) in guidedMessages" :key="`guided-${index}`" class="turn" :class="item.role">
          <strong>{{ item.role === "assistant" ? "assistant" : "you" }}</strong>
          <div style="margin-top: 4px">{{ item.text }}</div>
        </div>
      </div>

      <div v-if="guidedStep === 'prompt'" class="result-block" style="margin-top: 10px">
        <strong>실무 질문 예시</strong>
        <div style="display: flex; flex-direction: column; gap: 8px; margin-top: 8px">
          <button
            v-for="(example, index) in practicalQuestionExamples"
            :key="`example-${index}`"
            style="text-align: left"
            :disabled="isBusy"
            @click="applyPracticalExample(example)"
          >
            {{ example }}
          </button>
        </div>
      </div>

      <div class="result-block" style="margin-top: 10px">
        <strong>출력 언어 선택</strong>
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px">
          <button
            v-for="item in guidedLanguageOptions"
            :key="`guided-lang-${item.value}`"
            :class="guided.language === item.value ? 'primary' : ''"
            :disabled="isBusy"
            @click="setGuidedLanguage(item.value)"
          >
            {{ item.label }}
          </button>
        </div>
        <p class="muted" style="margin: 8px 0 0">현재 언어: {{ guided.language }}</p>
      </div>

      <label>
        대화 입력
        <input v-model="guidedInput" :placeholder="guidedPlaceholder" :disabled="isBusy" @keyup.enter="onGuidedSend" />
      </label>
      <div style="display: flex; gap: 8px; margin-top: 10px">
        <button class="primary" :disabled="isBusy || !guidedInput.trim()" @click="onGuidedSend">보내기</button>
        <button :disabled="isBusy" @click="resetGuidedConversation">대화 초기화</button>
      </div>

      <p class="muted" style="margin-top: 8px">간편 모드는 top_k를 5로 고정해 품질과 속도의 균형을 맞춥니다.</p>
    </template>

    <template v-else>
      <p class="muted" style="margin: 8px 0">상세 모드는 모든 필드를 직접 제어합니다.</p>

      <label>
        <span class="label-inline">
          <span>product_name</span>
          <span class="help-icon" title="광고/랜딩에서 반복 노출될 핵심 제품명입니다. 브랜드명/서비스명을 정확히 입력하세요.">?</span>
        </span>
        <input v-model="advanced.product_name" :disabled="isBusy" />
      </label>
      <label>
        target_audience
        <input v-model="advanced.target_audience" :disabled="isBusy" />
      </label>

      <label>
        <span class="label-inline">
          <span>pain_point</span>
          <span class="help-icon" title="고객이 현재 겪는 성과 문제입니다. 문제 상황 + 지표 손실(CTR/CVR/CAC) + 긴급성을 함께 적으세요.">?</span>
        </span>
        <textarea
          v-model="advanced.pain_point"
          rows="3"
          :disabled="isBusy"
          placeholder="타깃이 겪는 문제 상황 + 성과 손실 + 감정을 적어주세요"
        />
      </label>
      <p class="muted" style="margin: 4px 0 10px">
        정의: 고객이 지금 행동해야 하는 이유를 만드는 성과 문제입니다. 예: CTR 하락과 소재 피로로 CAC가 상승해, 동일 예산 대비 리드 확보량이 줄고 있다.
      </p>

      <label>
        <span class="label-inline">
          <span>differentiator</span>
          <span class="help-icon" title="경쟁 대비 성과 우위를 설명하는 문장입니다. 핵심 기능 + 근거 + 기대 성과를 한 번에 연결하세요.">?</span>
        </span>
        <textarea
          v-model="advanced.differentiator"
          rows="3"
          :disabled="isBusy"
          placeholder="경쟁 대비 차별점(기능+근거+결과)을 한 문장으로"
        />
      </label>
      <p class="muted" style="margin: 4px 0 10px">
        정의: 우리 솔루션이 더 높은 마케팅 성과를 내는 이유입니다. 예: RAG+Tavily 근거 결합으로 메시지 정확도와 최신성을 높여 전환형 카피 제작 시간을 단축한다.
      </p>

      <PromptOption
        v-model="advanced.objective"
        label="objective"
        help-text="카피의 1차 KPI 목표입니다. click은 CTR 중심, add_to_cart는 장바구니 전환 중심입니다."
        :options="objectiveOptions"
      />
      <p class="muted" style="margin: 4px 0 10px">{{ objectiveGuide[advanced.objective as Objective] }}</p>

      <PromptOption
        v-model="advanced.tone"
        label="tone"
        help-text="문장 톤 가이드입니다. 신뢰형(근거 중심), 도전형(강한 후킹), 친근형(가벼운 공감)"
        :options="toneOptions"
      />

      <label>
        <span class="label-inline">
          <span>channel</span>
          <span class="help-icon" title="카피가 실제 노출될 매체/지면입니다. 채널이 구체적일수록 문장 길이와 톤이 정확해집니다.">?</span>
        </span>
        <input v-model="advanced.channel" :disabled="isBusy" placeholder="예: 메타 광고 랜딩 / 인스타 피드 / 상세페이지" />
      </label>

      <PromptOption
        v-model="advanced.language"
        label="language"
        help-text="출력 언어 코드입니다. 예: ko, en, ja, zh-CN"
        :options="languageOptions"
      />

      <label>
        <span class="label-inline">
          <span>검색 근거 개수 (top_k)</span>
          <span class="help-icon" title="RAG/웹 검색에서 참고할 근거 개수입니다. 일반적으로 3~8이 안정적입니다.">?</span>
        </span>
        <input v-model.number="advanced.top_k" type="number" min="1" max="20" :disabled="isBusy" />
      </label>
      <p class="muted" style="margin: 4px 0 10px">
        top_k는 참고 근거 개수입니다. 작으면 근거가 빈약하고, 크면 문맥이 퍼질 수 있어 보통 3~8을 권장합니다.
      </p>

      <div style="margin-top: 8px">
        <span class="chip" v-for="style in Object.keys(advanced.styles)" :key="style">
          <input :id="`adv-style-${style}`" v-model="advanced.styles[style as Style]" type="checkbox" :disabled="isBusy" />
          <label :for="`adv-style-${style}`" style="margin-left: 6px">{{ style }}</label>
        </span>
      </div>

      <div style="margin-top: 8px">
        <span class="chip">
          <input id="adv-rag" v-model="advanced.use_rag" type="checkbox" :disabled="isBusy" />
          <label for="adv-rag" style="margin-left: 6px">use_rag</label>
        </span>
        <span class="chip">
          <input id="adv-web" v-model="advanced.web_search_mode" type="checkbox" :disabled="isBusy" />
          <label for="adv-web" style="margin-left: 6px">web_search_mode</label>
        </span>
      </div>

      <div style="margin-top: 10px; display: flex; gap: 8px">
        <button class="primary" :disabled="isBusy" @click="onGenerateAdvanced">카피 생성</button>
      </div>
    </template>

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
      <input v-model="advanced.landing_url" :disabled="isBusy" placeholder="https://example.com" />
    </label>
    <label>
      landing_query
      <input v-model="advanced.landing_query" :disabled="isBusy" placeholder="url 없을 때 Tavily 검색 쿼리" />
    </label>

    <button class="secondary" style="margin-top: 10px" :disabled="isBusy" @click="onAnalyze">랜딩 분석 실행</button>
  </div>
</template>
