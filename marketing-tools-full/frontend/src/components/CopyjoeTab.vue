<template>
  <div class="space-y-6">
    <!-- Copy Type Selection -->
    <div class="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
      <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
        <Sparkles class="text-orange-400" :size="20" />
        카피 유형 선택
      </h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <button
          v-for="type in copyTypes"
          :key="type.id"
          @click="copyType = type.id"
          :class="[
            'p-4 rounded-lg border transition-all text-left',
            copyType === type.id
              ? 'border-orange-500 bg-orange-500/20'
              : 'border-slate-600 hover:border-slate-500'
          ]"
        >
          <span class="text-2xl">{{ type.icon }}</span>
          <div class="font-medium mt-2">{{ type.name }}</div>
          <div class="text-xs text-slate-400">{{ type.desc }}</div>
        </button>
      </div>
    </div>

    <!-- Brand Info Input -->
    <div class="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
      <h2 class="text-xl font-semibold mb-4">📝 브랜드 정보 입력</h2>
      <div class="grid md:grid-cols-2 gap-4">
        <input
          v-model="copyInput.brand"
          placeholder="브랜드/제품명"
          class="w-full p-3 rounded-lg bg-slate-700 border border-slate-600 focus:border-orange-500 outline-none"
        />
        <input
          v-model="copyInput.target"
          placeholder="타겟 고객 (예: 30대 직장인 여성)"
          class="w-full p-3 rounded-lg bg-slate-700 border border-slate-600 focus:border-orange-500 outline-none"
        />
        <input
          v-model="copyInput.benefit"
          placeholder="핵심 혜택"
          class="w-full p-3 rounded-lg bg-slate-700 border border-slate-600 focus:border-orange-500 outline-none"
        />
        <input
          v-model="copyInput.problem"
          placeholder="고객의 문제/고민"
          class="w-full p-3 rounded-lg bg-slate-700 border border-slate-600 focus:border-orange-500 outline-none"
        />
      </div>

      <!-- File Upload -->
      <div class="mt-4 flex gap-3 items-center">
        <label class="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-700 cursor-pointer hover:bg-slate-600 transition">
          <Upload :size="18" />
          RAG 파일 업로드
          <input 
            type="file" 
            class="hidden" 
            accept=".txt,.md,.csv" 
            @change="handleFileUpload"
          />
        </label>
        <span v-if="uploadedFile" class="text-sm text-green-400 flex items-center gap-1">
          <Check :size="14" /> {{ uploadedFile.name }}
        </span>
      </div>

      <button
        @click="generateCopy"
        :disabled="loading || !copyInput.brand"
        class="mt-4 w-full py-3 rounded-lg bg-gradient-to-r from-orange-500 to-red-500 font-semibold hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
      >
        <RefreshCw v-if="loading" class="animate-spin" :size="18" />
        <Sparkles v-else :size="18" />
        카피 생성하기
      </button>
    </div>

    <!-- Generated Copies -->
    <div v-if="copyResults.length > 0" class="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
      <h2 class="text-xl font-semibold mb-4">✨ 생성된 카피</h2>
      <div class="space-y-3">
        <div
          v-for="(item, idx) in copyResults"
          :key="idx"
          class="p-4 rounded-lg bg-slate-700/50 border border-slate-600 group"
        >
          <div class="flex justify-between items-start">
            <p class="text-lg font-medium text-orange-300">"{{ item.copy }}"</p>
            <button
              @click="handleCopy(item.copy)"
              class="opacity-0 group-hover:opacity-100 p-1 hover:bg-slate-600 rounded transition"
            >
              <Copy :size="16" />
            </button>
          </div>
          <p v-if="item.rationale" class="text-sm text-slate-400 mt-2">💡 {{ item.rationale }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Sparkles, Upload, Check, RefreshCw, Copy } from 'lucide-vue-next'
import { useApi } from '../composables/useApi'

const { loading, generateCopy: apiGenerateCopy, uploadRagFile, copyToClipboard } = useApi()

const copyType = ref('slogan')
const copyInput = reactive({
  brand: '',
  target: '',
  benefit: '',
  problem: ''
})
const copyResults = ref([])
const uploadedFile = ref(null)

const copyTypes = [
  { id: 'slogan', name: '슬로건형', desc: '브랜드 이미지 각인', icon: '🎯' },
  { id: 'problem', name: '문제 해결형', desc: '고객 고민 건드리기', icon: '💡' },
  { id: 'benefit', name: '혜택 강조형', desc: '결과를 먼저 보여주기', icon: '🎁' },
  { id: 'cta', name: 'CTA형', desc: '행동 직접 요구', icon: '👆' },
]

const handleFileUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  try {
    const result = await uploadRagFile(file)
    uploadedFile.value = {
      name: result.filename,
      content: result.content
    }
  } catch (err) {
    console.error('File upload failed:', err)
  }
}

const generateCopy = async () => {
  try {
    const result = await apiGenerateCopy({
      copyType: copyType.value,
      brand: copyInput.brand,
      target: copyInput.target,
      benefit: copyInput.benefit,
      problem: copyInput.problem,
      ragContent: uploadedFile.value?.content || ''
    })
    copyResults.value = result
  } catch (err) {
    copyResults.value = [{ copy: '오류가 발생했습니다.', rationale: err.message }]
  }
}

const handleCopy = async (text) => {
  await copyToClipboard(text)
}
</script>
