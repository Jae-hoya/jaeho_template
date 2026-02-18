<template>
  <div class="loading-inline muted" role="status" aria-live="polite" aria-label="처리 중">
    <span class="loading-dot" aria-hidden="true" />
    <span>처리 중...</span>
  </div>
</template>

<style scoped>
.loading-inline {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.loading-dot {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  border: 2px solid #b7c8ea;
  border-top-color: #2f5ecf;
  animation: loading-spin 0.9s linear infinite;
}

@keyframes loading-spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
