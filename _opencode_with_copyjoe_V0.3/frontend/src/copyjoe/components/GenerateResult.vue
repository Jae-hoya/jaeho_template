<script setup lang="ts">
import { ref } from "vue"

import type { CopyGenerateResponse } from "../models-service/types"
import ExportDialog from "./ExportDialog.vue"

const props = defineProps<{
  result: CopyGenerateResponse
}>()

const showExportDialog = ref(false)

function copy(text: string) {
  if (!text) {
    return
  }
  void navigator.clipboard.writeText(text)
}
</script>

<template>
  <div>
    <div class="result-block">
      <strong>head</strong>
      <p>{{ result.head }}</p>
      <button @click="copy(result.head)">복사</button>
    </div>
    <div class="result-block">
      <strong>body</strong>
      <p>{{ result.body }}</p>
      <button @click="copy(result.body)">복사</button>
    </div>
    <div class="result-block">
      <strong>cta</strong>
      <p>{{ result.cta }}</p>
      <button @click="copy(result.cta)">복사</button>
    </div>
    <div class="result-block">
      <strong>slogan</strong>
      <p>{{ result.slogan }}</p>
      <button @click="copy(result.slogan)">복사</button>
    </div>
    <div class="result-block">
      <strong>sns</strong>
      <p>{{ result.sns }}</p>
      <button @click="copy(result.sns)">복사</button>
    </div>
    <div class="result-block">
      <strong>description</strong>
      <p>{{ result.description }}</p>
      <button @click="copy(result.description)">복사</button>
    </div>

    <div class="result-block">
      <strong>storyboard_outline</strong>
      <ul>
        <li v-for="(line, index) in result.storyboard_outline" :key="`${index}-${line}`">{{ line }}</li>
      </ul>
    </div>

    <div class="result-block">
      <strong>rationale</strong>
      <p>{{ result.rationale }}</p>
    </div>

    <div class="result-block">
      <strong>sources</strong>
      <ul>
        <li v-for="(source, index) in result.sources" :key="`${source.source_type}-${index}`">
          [{{ source.source_type }}] {{ source.title || "untitled" }} {{ source.url || "" }}
        </li>
      </ul>
    </div>

    <button class="secondary" @click="showExportDialog = !showExportDialog">Word Export</button>
    <ExportDialog :open="showExportDialog" :result="result" @close="showExportDialog = false" />
  </div>
</template>
