<script setup lang="ts">
defineProps<{
  label: string
  helpText?: string
  modelValue: string
  options: Array<{ label: string; value: string }>
}>()

const emit = defineEmits<{
  "update:modelValue": [value: string]
}>()

function onChange(event: Event) {
  const target = event.target as HTMLSelectElement
  emit("update:modelValue", target.value)
}
</script>

<template>
  <label>
    <span class="label-inline">
      <span>{{ label }}</span>
      <span v-if="helpText" class="help-icon" :title="helpText">?</span>
    </span>
    <select :value="modelValue" @change="onChange">
      <option v-for="item in options" :key="item.value" :value="item.value">
        {{ item.label }}
      </option>
    </select>
  </label>
</template>
