<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 text-white p-4">
    <div class="max-w-6xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold bg-gradient-to-r from-orange-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
          Marketing Tools Suite
        </h1>
        <p class="text-slate-400 mt-2">카피조 • Chenius Chat • Brief Reader</p>
      </div>

      <!-- Tab Navigation -->
      <div class="flex gap-2 mb-6 justify-center flex-wrap">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          @click="activeTab = tab.id"
          :class="[
            'flex items-center gap-2 px-4 py-2 rounded-lg transition-all',
            activeTab === tab.id
              ? `bg-gradient-to-r ${tab.color} shadow-lg`
              : 'bg-slate-700/50 hover:bg-slate-700'
          ]"
        >
          <component :is="tab.icon" :size="18" />
          {{ tab.name }}
        </button>
      </div>

      <!-- Copyjoe Tab -->
      <CopyjoeTab v-if="activeTab === 'copyjoe'" />

      <!-- Chenius Chat Tab -->
      <CheniusChatTab v-if="activeTab === 'chenius'" />

      <!-- Brief Reader Tab -->
      <BriefReaderTab v-if="activeTab === 'brief'" />
    </div>
  </div>
</template>

<script setup>
import { ref, markRaw } from 'vue'
import { PenTool, MessageSquare, FileText } from 'lucide-vue-next'
import CopyjoeTab from './components/CopyjoeTab.vue'
import CheniusChatTab from './components/CheniusChatTab.vue'
import BriefReaderTab from './components/BriefReaderTab.vue'

const activeTab = ref('copyjoe')

const tabs = [
  { id: 'copyjoe', name: '카피조', icon: markRaw(PenTool), color: 'from-orange-500 to-red-500' },
  { id: 'chenius', name: 'Chenius Chat', icon: markRaw(MessageSquare), color: 'from-blue-500 to-purple-500' },
  { id: 'brief', name: 'Brief Reader', icon: markRaw(FileText), color: 'from-green-500 to-teal-500' },
]
</script>

<style>
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';
</style>
