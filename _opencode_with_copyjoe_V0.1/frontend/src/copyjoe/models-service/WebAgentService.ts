import { analyzeLanding } from "./service"
import type { LandingAnalyzeRequest, LandingAnalyzeResponse } from "./types"

class WebAgentService {
  async analyze(payload: LandingAnalyzeRequest): Promise<LandingAnalyzeResponse> {
    return analyzeLanding(payload)
  }

  async analyzeByUrl(url: string): Promise<LandingAnalyzeResponse> {
    return analyzeLanding({ url })
  }

  async analyzeByQuery(query: string): Promise<LandingAnalyzeResponse> {
    return analyzeLanding({ query, max_results: 5 })
  }
}

export const webAgentService = new WebAgentService()
