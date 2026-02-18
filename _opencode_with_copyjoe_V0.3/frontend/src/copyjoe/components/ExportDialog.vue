<script setup lang="ts">
import { ref } from "vue"

import { exportCopyDoc, exportCopyDocx, exportCopyMarkdown } from "../models-service/service"
import type { CopyGenerateResponse } from "../models-service/types"

const props = defineProps<{
  open: boolean
  result: CopyGenerateResponse
}>()

const emit = defineEmits<{
  close: []
}>()

const fileName = ref("copyjoe_output.docx")
const fileType = ref<"docx" | "doc" | "md">("docx")
const loading = ref(false)
const errorMessage = ref("")

function resolvedFileName(type: "docx" | "doc" | "md", name: string): string {
  const trimmed = name.trim() || "copyjoe_output"
  if (trimmed.toLowerCase().endsWith(`.${type}`)) {
    return trimmed
  }
  return `${trimmed}.${type}`
}

async function onExport() {
  loading.value = true
  errorMessage.value = ""

  try {
    const finalName = resolvedFileName(fileType.value, fileName.value)
    let blob: Blob

    if (fileType.value === "docx") {
      blob = await exportCopyDocx({
        file_name: finalName,
        result: props.result,
      })
    } else if (fileType.value === "doc") {
      blob = await exportCopyDoc({
        file_name: finalName,
        result: props.result,
      })
    } else {
      blob = await exportCopyMarkdown({
        file_name: finalName,
        result: props.result,
      })
    }

    const url = window.URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = finalName
    a.click()
    window.URL.revokeObjectURL(url)
    emit("close")
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : "export failed"
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div v-if="open" class="card" style="margin-top: 10px">
    <label>
      형식
      <select v-model="fileType">
        <option value="docx">docx</option>
        <option value="doc">doc</option>
        <option value="md">md</option>
      </select>
    </label>
    <label>
      파일명
      <input v-model="fileName" />
    </label>
    <div style="margin-top: 10px; display: flex; gap: 8px">
      <button class="primary" :disabled="loading" @click="onExport">내보내기</button>
      <button @click="emit('close')">닫기</button>
    </div>
    <p v-if="errorMessage" class="muted">{{ errorMessage }}</p>
  </div>
</template>
