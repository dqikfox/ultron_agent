
import axios from 'axios'

export class OllamaService {
  private baseUrl = 'http://localhost:11434'

  async getModels() {
    try {
      const response = await axios.get(`${this.baseUrl}/api/tags`)
      return response.data.models || []
    } catch (error) {
      console.error('Failed to get Ollama models:', error)
      return []
    }
  }

  async chatWithModel(modelName: string, messages: any[]) {
    try {
      console.log('Sending to Ollama:', { modelName, messageCount: messages.length })
      
      const response = await axios.post(`${this.baseUrl}/api/chat`, {
        model: modelName,
        messages: messages,
        stream: false
      })

      const content = response.data.message?.content || 'No response from model'
      console.log('Ollama response:', content.substring(0, 100) + '...')
      
      return content
    } catch (error) {
      console.error('Chat with model failed:', error)
      throw new Error(`Failed to chat with model ${modelName}: ${error.message}`)
    }
  }
}
