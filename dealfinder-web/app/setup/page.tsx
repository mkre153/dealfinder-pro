'use client'

import { useState, useRef, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { Bot, User, Send, Loader2, CheckCircle, MapPin, DollarSign, Home } from 'lucide-react'
import { sendChatMessage, createAgent } from '@/lib/api-client'
import type { ChatMessage, AgentCriteria } from '@/lib/types'

export default function SetupPage() {
  const router = useRouter()
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [suggestedCriteria, setSuggestedCriteria] = useState<AgentCriteria | null>(null)
  const [clientName, setClientName] = useState('')
  const [clientEmail, setClientEmail] = useState('')
  const [isCreatingAgent, setIsCreatingAgent] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Initial AI greeting
    setMessages([
      {
        role: 'assistant',
        content: 'Hi there. I\'m your Senior Acquisition Specialist. Let\'s configure your property search agent.\n\nFirst, what type of properties are you targeting?',
        timestamp: new Date().toISOString(),
      },
    ])
  }, [])

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputValue,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await sendChatMessage({
        message: inputValue,
        conversation_history: messages,
      })

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, assistantMessage])

      // Check if agent configuration is ready
      if (response.agent_configured && response.suggested_criteria) {
        setSuggestedCriteria(response.suggested_criteria)
      }
    } catch (error: any) {
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error.error || 'Unknown error'}`,
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreateAgent = async () => {
    if (!suggestedCriteria || !clientName) return

    setIsCreatingAgent(true)

    try {
      const agent = await createAgent({
        client_name: clientName,
        client_email: clientEmail || undefined,
        criteria: suggestedCriteria,
        notification_email: true,
        notification_sms: false,
        notification_chat: true,
      })

      // Show success and redirect
      alert(`🎉 Agent created successfully!\n\nAgent ID: ${agent.agent_id}\n\nYour agent is now monitoring properties 24/7. Matches will appear in your GoHighLevel opportunities.`)

      // In production, redirect to GHL or success page
      router.push('/')
    } catch (error: any) {
      alert(`Error creating agent: ${error.error || 'Unknown error'}`)
    } finally {
      setIsCreatingAgent(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex flex-col">
      {/* Header */}
      <header className="border-b border-blue-400/20 bg-slate-900/50 backdrop-blur">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Bot className="h-6 w-6 text-blue-400" />
              <h1 className="text-xl font-semibold text-white">Agent Configuration</h1>
            </div>
            <div className="text-sm text-blue-200">Step 1 of 1</div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 container mx-auto px-6 py-8 flex flex-col lg:flex-row gap-8">
        {/* Chat Section */}
        <div className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 space-y-6 overflow-y-auto mb-6 pr-4" style={{ maxHeight: 'calc(100vh - 300px)' }}>
            <AnimatePresence>
              {messages.map((msg, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start space-x-3 max-w-2xl ${msg.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''}`}>
                    {/* Avatar */}
                    <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                      msg.role === 'user' ? 'bg-blue-500' : 'bg-gradient-to-br from-cyan-500 to-blue-600'
                    }`}>
                      {msg.role === 'user' ? <User className="h-5 w-5 text-white" /> : <Bot className="h-5 w-5 text-white" />}
                    </div>

                    {/* Message Content */}
                    <div className={`px-4 py-3 rounded-2xl ${
                      msg.role === 'user'
                        ? 'bg-blue-500 text-white'
                        : 'bg-white/10 text-blue-50 backdrop-blur'
                    }`}>
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center">
                    <Bot className="h-5 w-5 text-white" />
                  </div>
                  <div className="px-4 py-3 rounded-2xl bg-white/10 backdrop-blur">
                    <Loader2 className="h-5 w-5 text-blue-400 animate-spin" />
                  </div>
                </div>
              </motion.div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="flex items-end space-x-3">
            <textarea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              disabled={isLoading || !!suggestedCriteria}
              rows={2}
              className="flex-1 px-4 py-3 bg-white/10 backdrop-blur border border-blue-400/20 rounded-2xl text-white placeholder-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 resize-none"
            />
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading || !!suggestedCriteria}
              className="p-3 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 rounded-full text-white transition-colors disabled:cursor-not-allowed"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Criteria Review Panel */}
        <AnimatePresence>
          {suggestedCriteria && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="lg:w-96 space-y-6"
            >
              <div className="glass-dark rounded-2xl p-6 space-y-6">
                <div className="flex items-center space-x-2 text-green-400">
                  <CheckCircle className="h-6 w-6" />
                  <h2 className="text-xl font-semibold text-white">Configuration Ready</h2>
                </div>

                {/* Criteria Display */}
                <div className="space-y-4">
                  {suggestedCriteria.zip_codes && suggestedCriteria.zip_codes.length > 0 && (
                    <div className="flex items-start space-x-3">
                      <MapPin className="h-5 w-5 text-blue-400 mt-1" />
                      <div>
                        <p className="text-sm text-blue-300 font-medium">Locations</p>
                        <p className="text-white">{suggestedCriteria.zip_codes.join(', ')}</p>
                      </div>
                    </div>
                  )}

                  {(suggestedCriteria.price_min || suggestedCriteria.price_max) && (
                    <div className="flex items-start space-x-3">
                      <DollarSign className="h-5 w-5 text-green-400 mt-1" />
                      <div>
                        <p className="text-sm text-blue-300 font-medium">Price Range</p>
                        <p className="text-white">
                          {suggestedCriteria.price_min ? `$${(suggestedCriteria.price_min / 1000).toFixed(0)}K` : 'Any'} - {suggestedCriteria.price_max ? `$${(suggestedCriteria.price_max / 1000).toFixed(0)}K` : 'Any'}
                        </p>
                      </div>
                    </div>
                  )}

                  {(suggestedCriteria.bedrooms_min || suggestedCriteria.bathrooms_min) && (
                    <div className="flex items-start space-x-3">
                      <Home className="h-5 w-5 text-purple-400 mt-1" />
                      <div>
                        <p className="text-sm text-blue-300 font-medium">Property Size</p>
                        <p className="text-white">
                          {suggestedCriteria.bedrooms_min && `${suggestedCriteria.bedrooms_min}+ beds`}
                          {suggestedCriteria.bedrooms_min && suggestedCriteria.bathrooms_min && ', '}
                          {suggestedCriteria.bathrooms_min && `${suggestedCriteria.bathrooms_min}+ baths`}
                        </p>
                      </div>
                    </div>
                  )}

                  {suggestedCriteria.investment_type && (
                    <div className="px-3 py-2 bg-blue-500/20 rounded-lg border border-blue-400/30">
                      <p className="text-sm text-blue-200">
                        <span className="font-medium">Strategy:</span> {suggestedCriteria.investment_type.replace('_', ' ')}
                      </p>
                    </div>
                  )}
                </div>

                {/* Client Info Form */}
                <div className="space-y-3 pt-4 border-t border-blue-400/20">
                  <input
                    type="text"
                    value={clientName}
                    onChange={(e) => setClientName(e.target.value)}
                    placeholder="Your Name *"
                    className="w-full px-4 py-2 bg-white/10 border border-blue-400/20 rounded-lg text-white placeholder-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <input
                    type="email"
                    value={clientEmail}
                    onChange={(e) => setClientEmail(e.target.value)}
                    placeholder="Email (optional)"
                    className="w-full px-4 py-2 bg-white/10 border border-blue-400/20 rounded-lg text-white placeholder-blue-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Create Button */}
                <button
                  onClick={handleCreateAgent}
                  disabled={!clientName || isCreatingAgent}
                  className="w-full py-3 bg-gradient-to-r from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600 disabled:from-gray-600 disabled:to-gray-600 rounded-lg text-white font-semibold transition-all disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                >
                  {isCreatingAgent ? (
                    <>
                      <Loader2 className="h-5 w-5 animate-spin" />
                      <span>Creating Agent...</span>
                    </>
                  ) : (
                    <>
                      <CheckCircle className="h-5 w-5" />
                      <span>Create Agent</span>
                    </>
                  )}
                </button>

                <p className="text-xs text-blue-300 text-center">
                  Your agent will start monitoring immediately and check properties every 4 hours.
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
