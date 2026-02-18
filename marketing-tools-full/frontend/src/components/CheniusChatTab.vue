<template>
  <div class="space-y-6">
    <!-- Dual Chat Windows -->
    <div class="grid md:grid-cols-2 gap-4">
      <div
        v-for="(modelKey, idx) in ['model1', 'model2']"
        :key="modelKey"
        class="bg-slate-800/50 rounded-xl p-4 border border-slate-700"
      >
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-semibold flex items-center gap-2">
            {{ idx === 0 ? '🎨 창의적 관점' : '📊 실용적 관점' }}
          </h3>
          <button
            v-if="chatResults[modelKey].length > 0"
            @click="selectBestResponse(modelKey)"
            :class="[
              'px-3 py-1 rounded-lg text-sm transition',
              selectedModel === modelKey
                ? 'bg-green-500 text-white'
                : 'bg-slate-600 hover:bg-slate-500'
            ]"
          >
            <Check v-if="selectedModel === modelKey" :size="14" />
            <span v-else>Select</span>
          </button>
        </div>
        
        <div class="h-64 overflow-y-auto space-y-2 mb-3 p-2 bg-slate-900/50 rounded-lg">
          <div
            v-for="(msg, i) in chatResults[modelKey]"
            :key="i"
            :class="[
              'p-2 rounded text-sm',
              msg.role === 'user'
                ? 'bg-blue-600/30 ml-8'
                : 'bg-slate-700/50 mr-8'
            ]"
          >
            {{ msg.content }}
          </div>
          <p v-if="chatResults[modelKey].length === 0" class="text-slate-500 text-center py-8">
            대화를 시작하세요
          </p>
        </div>
      </div>
    </div>

    <!-- Input Area -->
    <div class="flex gap-3">
      <input
        v-model="chatInput"
        @keypress.enter="runCheniusChat"
        placeholder="마케팅 아이디어나 질문을 입력하세요..."
        class="flex-1 p-3 rounded-lg bg-slate-700 border border-slate-600 focus:border-blue-500 outline-none"
      />
      <button
        @click="runCheniusChat"
        :disabled="loading || !chatInput.trim()"
        class="px-6 py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-500 font-semibold hover:opacity-90 disabled:opacity-50"
      >
        <RefreshCw v-if="loading" class="animate-spin" :size="18" />
        <ChevronRight v-else :size="18" />
      </button>
    </div>

    <!-- Chat History -->
    <div v-if="chatHistory.length > 0" class="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
      <h3 class="font-semibold mb-2">📜 선택된 대화 히스토리</h3>
      <div class="space-y-2 text-sm">
        <div
          v-for="(msg, i) in chatHistory.slice(-4)"
          :key="i"
          :class="['p-2 rounded', msg.role === 'user' ? 'bg-blue-600/20' : 'bg-green-600/20']"
        >
          <span class="font-medium">{{ msg.role === 'user' ? '👤' : '🤖' }}</span>
          {{ msg.content.slice(0, 100) }}...
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { Check, RefreshCw, ChevronRight } from 'lucide-vue-next'
import { useApi } from '../composables/useApi'

const { loading, cheniusChat } = useApi()

const chatInput = ref('')
const chatResults = reactive({
  model1: [],
  model2: []
})
const selectedModel = ref(null)
const chatHistory = ref([])

const runCheniusChat = async () => {
  if (!chatInput.value.trim()) return

  try {
    const { creative, practical } = await cheniusChat(
      chatInput.value,
      chatHistory.value
    )

    chatResults.model1.push(
      { role: 'user', content: chatInput.value },
      { role: 'assistant', content: creative }
    )
    chatResults.model2.push(
      { role: 'user', content: chatInput.value },
      { role: 'assistant', content: practical }
    )

    chatInput.value = ''
    selectedModel.value = null
  } catch (err) {
    console.error('Chat failed:', err)
  }
}

const selectBestResponse = (modelKey) => {
  const messages = chatResults[modelKey]
  const lastResponse = messages[messages.length - 1]
  
  if (lastResponse?.role === 'assistant') {
    const userMessage = messages[messages.length - 2]
    chatHistory.value.push(
      { role: 'user', content: userMessage?.content },
      { role: 'assistant', content: lastResponse.content }
    )
    selectedModel.value = modelKey
  }
}
</script>
