import { ref } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  /**
   * Generic API call wrapper
   */
  const apiCall = async (endpoint, options = {}) => {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      })
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`)
      }
      
      return await response.json()
    } catch (err) {
      error.value = err.message
      throw err
    }
  }

  /**
   * Copyjoe - 카피 생성
   */
  const generateCopy = async ({ copyType, brand, target, benefit, problem, ragContent }) => {
    loading.value = true
    error.value = null
    
    try {
      const result = await apiCall('/api/copyjoe/generate', {
        method: 'POST',
        body: JSON.stringify({
          copy_type: copyType,
          brand,
          target,
          benefit,
          problem,
          rag_content: ragContent || ''
        })
      })
      return result.copies
    } finally {
      loading.value = false
    }
  }

  /**
   * Copyjoe - RAG 파일 업로드
   */
  const uploadRagFile = async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await fetch(`${API_BASE_URL}/api/copyjoe/upload-rag`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      throw new Error('File upload failed')
    }
    
    return await response.json()
  }

  /**
   * Chenius Chat - 듀얼 AI 채팅
   */
  const cheniusChat = async (message, history = []) => {
    loading.value = true
    error.value = null
    
    try {
      const result = await apiCall('/api/chenius/chat', {
        method: 'POST',
        body: JSON.stringify({ message, history })
      })
      return {
        creative: result.creative,
        practical: result.practical
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * Brief Reader - 브리프 분석
   */
  const analyzeBrief = async (content) => {
    loading.value = true
    error.value = null
    
    try {
      const result = await apiCall('/api/brief/analyze', {
        method: 'POST',
        body: JSON.stringify({ content })
      })
      return result
    } finally {
      loading.value = false
    }
  }

  /**
   * Brief Reader - 파일 업로드
   */
  const uploadBriefFile = async (file) => {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await fetch(`${API_BASE_URL}/api/brief/upload`, {
      method: 'POST',
      body: formData
    })
    
    if (!response.ok) {
      throw new Error('File upload failed')
    }
    
    return await response.json()
  }

  /**
   * Health check
   */
  const healthCheck = async () => {
    return await apiCall('/health')
  }

  /**
   * Clipboard utility
   */
  const copyToClipboard = async (text) => {
    try {
      await navigator.clipboard.writeText(text)
      return true
    } catch {
      return false
    }
  }

  return {
    // State
    loading,
    error,
    
    // Copyjoe
    generateCopy,
    uploadRagFile,
    
    // Chenius Chat
    cheniusChat,
    
    // Brief Reader
    analyzeBrief,
    uploadBriefFile,
    
    // Utils
    healthCheck,
    copyToClipboard
  }
}
