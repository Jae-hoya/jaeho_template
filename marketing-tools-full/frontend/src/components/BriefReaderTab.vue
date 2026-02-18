<template>
  <div class="space-y-6">
    <!-- Input Section -->
    <div class="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
      <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
        <FileText class="text-green-400" :size="20" />
        클라이언트 브리프 입력
      </h2>
      
      <!-- File Upload -->
      <label class="flex items-center gap-2 px-4 py-3 rounded-lg bg-slate-700 cursor-pointer hover:bg-slate-600 transition mb-4 w-fit">
        <Upload :size="18" />
        브리프 파일 업로드
        <input 
          type="file" 
          class="hidden" 
          accept=".txt,.md,.pdf" 
          @change="handleFileUpload"
        />
      </label>
      <p v-if="briefFile" class="text-sm text-green-400 mb-2 flex items-center gap-1">
        <Check :size="14" /> {{ briefFile.name }}
      </p>

      <!-- Text Input -->
      <textarea
        v-model="briefText"
        placeholder="또는 브리프 내용을 직접 붙여넣기..."
        class="w-full h-40 p-3 rounded-lg bg-slate-700 border border-slate-600 focus:border-green-500 outline-none resize-none"
      />

      <button
        @click="analyzeBrief"
        :disabled="loading || (!briefText.trim() && !briefFile)"
        class="mt-4 w-full py-3 rounded-lg bg-gradient-to-r from-green-500 to-teal-500 font-semibold hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2"
      >
        <RefreshCw v-if="loading" class="animate-spin" :size="18" />
        <FileText v-else :size="18" />
        브리프 분석하기
      </button>
    </div>

    <!-- Summary Section -->
    <div v-if="briefSummary" class="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
      <h2 class="text-xl font-semibold mb-4">📋 브리프 요약</h2>
      <div class="grid md:grid-cols-2 gap-4">
        <!-- Company -->
        <div v-if="briefSummary.company" class="p-3 rounded-lg bg-slate-700/50">
          <span class="text-slate-400 text-sm">회사명</span>
          <p class="font-medium">{{ briefSummary.company }}</p>
        </div>
        
        <!-- Product -->
        <div v-if="briefSummary.product" class="p-3 rounded-lg bg-slate-700/50">
          <span class="text-slate-400 text-sm">제품/서비스</span>
          <p class="font-medium">{{ briefSummary.product }}</p>
        </div>
        
        <!-- Target -->
        <div v-if="briefSummary.target" class="p-3 rounded-lg bg-slate-700/50">
          <span class="text-slate-400 text-sm">타겟 고객</span>
          <p class="font-medium">{{ briefSummary.target }}</p>
        </div>
        
        <!-- USP -->
        <div v-if="briefSummary.usp" class="p-3 rounded-lg bg-slate-700/50">
          <span class="text-slate-400 text-sm">차별점 (USP)</span>
          <p class="font-medium">{{ briefSummary.usp }}</p>
        </div>
        
        <!-- Problem -->
        <div v-if="briefSummary.problem" class="p-3 rounded-lg bg-slate-700/50 md:col-span-2">
          <span class="text-slate-400 text-sm">해결 문제</span>
          <p class="font-medium">{{ briefSummary.problem }}</p>
        </div>
        
        <!-- Goals -->
        <div v-if="briefSummary.goals" class="p-3 rounded-lg bg-slate-700/50">
          <span class="text-slate-400 text-sm">목표</span>
          <div class="flex flex-wrap gap-2 mt-1">
            <span
              v-for="(goal, i) in briefSummary.goals"
              :key="i"
              class="px-2 py-1 bg-green-600/30 rounded text-sm"
            >
              {{ goal }}
            </span>
          </div>
        </div>
        
        <!-- Keywords -->
        <div v-if="briefSummary.keywords" class="p-3 rounded-lg bg-slate-700/50">
          <span class="text-slate-400 text-sm">키워드</span>
          <div class="flex flex-wrap gap-2 mt-1">
            <span
              v-for="(keyword, i) in briefSummary.keywords"
              :key="i"
              class="px-2 py-1 bg-blue-600/30 rounded text-sm"
            >
              {{ keyword }}
            </span>
          </div>
        </div>
        
        <!-- Insights -->
        <div v-if="briefSummary.insights" class="p-3 rounded-lg bg-gradient-to-r from-purple-600/20 to-pink-600/20 md:col-span-2">
          <span class="text-slate-400 text-sm">💡 전략적 인사이트</span>
          <p class="font-medium mt-1">{{ briefSummary.insights }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { FileText, Upload, Check, RefreshCw } from 'lucide-vue-next'
import { useApi } from '../composables/useApi'

const { loading, analyzeBrief: apiAnalyzeBrief, uploadBriefFile } = useApi()

const briefFile = ref(null)
const briefText = ref('')
const briefSummary = ref(null)

const handleFileUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  try {
    const result = await uploadBriefFile(file)
    briefFile.value = { name: result.filename }
    briefText.value = result.content
  } catch (err) {
    console.error('File upload failed:', err)
  }
}

const analyzeBrief = async () => {
  if (!briefText.value.trim() && !briefFile.value) return

  try {
    const result = await apiAnalyzeBrief(briefText.value)
    briefSummary.value = result
  } catch (err) {
    briefSummary.value = { insights: '분석 중 오류가 발생했습니다: ' + err.message }
  }
}
</script>
