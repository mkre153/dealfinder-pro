'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Sparkles, Target, Zap, CheckCircle2, ArrowRight, Bot } from 'lucide-react'

export default function HomePage() {
  const [isReady, setIsReady] = useState(false)

  useEffect(() => {
    setIsReady(true)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -inset-[10px] opacity-50">
          {[...Array(20)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute h-px w-px bg-blue-400"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
              animate={{
                scale: [1, 2, 1],
                opacity: [0, 1, 0],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                delay: Math.random() * 2,
              }}
            />
          ))}
        </div>
      </div>

      {/* Header */}
      <header className="relative z-10 container mx-auto px-6 py-8">
        <nav className="flex items-center justify-between">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center space-x-2"
          >
            <Bot className="h-8 w-8 text-blue-400" />
            <span className="text-2xl font-bold text-white">DealFinder Pro</span>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-sm text-blue-200"
          >
            For GoHighLevel Users
          </motion.div>
        </nav>
      </header>

      {/* Hero Section */}
      <section className="relative z-10 container mx-auto px-6 pt-20 pb-32">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: isReady ? 1 : 0, y: isReady ? 0 : 20 }}
            transition={{ duration: 0.6 }}
            className="text-center space-y-8"
          >
            {/* Badge */}
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center space-x-2 px-4 py-2 rounded-full bg-blue-500/20 border border-blue-400/30 text-blue-200 text-sm"
            >
              <Sparkles className="h-4 w-4" />
              <span>AI-Powered Property Intelligence</span>
            </motion.div>

            {/* Headline */}
            <h1 className="text-5xl md:text-7xl font-bold text-white leading-tight">
              AI Property Scout
              <br />
              <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                For GoHighLevel
              </span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl md:text-2xl text-blue-100 max-w-3xl mx-auto">
              Chat with AI for 3 minutes. Get an autonomous agent that monitors properties 24/7
              and sends matches directly to your GoHighLevel CRM.
            </p>

            {/* CTA Button */}
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center pt-8"
            >
              <Link href="/setup">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="group px-8 py-4 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-full text-white font-semibold text-lg shadow-lg shadow-blue-500/50 hover:shadow-blue-500/70 transition-all flex items-center space-x-2"
                >
                  <span>Start with AI</span>
                  <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                </motion.button>
              </Link>

              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6 }}
                className="text-blue-200 text-sm"
              >
                Free setup • 3 minute configuration
              </motion.div>
            </motion.div>
          </motion.div>

          {/* How It Works */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: isReady ? 1 : 0, y: isReady ? 0 : 40 }}
            transition={{ delay: 0.6, duration: 0.6 }}
            className="mt-32 grid grid-cols-1 md:grid-cols-3 gap-8"
          >
            {[
              {
                icon: Target,
                title: 'Chat with AI',
                description: 'Tell Claude what properties you\'re looking for. Takes 3-5 minutes.',
                color: 'from-blue-500 to-blue-600',
              },
              {
                icon: Zap,
                title: 'Agent Monitors 24/7',
                description: 'Your autonomous agent checks properties every 4 hours automatically.',
                color: 'from-cyan-500 to-cyan-600',
              },
              {
                icon: CheckCircle2,
                title: 'Matches in GHL',
                description: 'Properties appear as opportunities in your GoHighLevel pipeline.',
                color: 'from-teal-500 to-teal-600',
              },
            ].map((step, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.8 + i * 0.1 }}
                className="glass-dark rounded-2xl p-8 space-y-4 hover:bg-white/10 transition-all"
              >
                <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${step.color}`}>
                  <step.icon className="h-6 w-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white">{step.title}</h3>
                <p className="text-blue-200">{step.description}</p>
              </motion.div>
            ))}
          </motion.div>

          {/* Social Proof */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
            className="mt-20 text-center space-y-4"
          >
            <p className="text-blue-300 text-sm uppercase tracking-wider">Perfect for</p>
            <div className="flex flex-wrap justify-center gap-4">
              {['Real Estate Investors', 'Property Wholesalers', 'Real Estate Agents', 'GHL Users'].map((tag) => (
                <span
                  key={tag}
                  className="px-4 py-2 rounded-full bg-blue-500/10 border border-blue-400/20 text-blue-200 text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative z-10 border-t border-blue-400/20 py-8">
        <div className="container mx-auto px-6 text-center text-blue-300 text-sm">
          <p>Powered by Claude AI • Built for GoHighLevel</p>
        </div>
      </footer>
    </div>
  )
}
