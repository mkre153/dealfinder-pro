import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'DealFinder Pro - AI Property Scout for GoHighLevel',
  description: 'Autonomous property search agents powered by AI. Configure once, get matches in GoHighLevel forever.',
  keywords: ['real estate', 'AI', 'property search', 'GoHighLevel', 'investment'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <main className="min-h-screen">
          {children}
        </main>
      </body>
    </html>
  )
}
