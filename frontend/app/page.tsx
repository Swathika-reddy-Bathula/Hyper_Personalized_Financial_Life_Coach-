'use client'

import { useState, useEffect } from 'react'
import ChatInterface from '@/components/ChatInterface'
import GoalsDashboard from '@/components/GoalsDashboard'
import BudgetInsights from '@/components/BudgetInsights'
import Recommendations from '@/components/Recommendations'
import Alerts from '@/components/Alerts'
import { Wallet, Target, TrendingUp, Bell } from 'lucide-react'

export default function Home() {
  const [activeTab, setActiveTab] = useState('chat')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    // Check for stored token
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      setToken(storedToken)
      setIsAuthenticated(true)
    }
  }, [])

  const tabs = [
    { id: 'chat', label: 'Chat', icon: Wallet },
    { id: 'goals', label: 'Goals', icon: Target },
    { id: 'insights', label: 'Insights', icon: TrendingUp },
    { id: 'alerts', label: 'Alerts', icon: Bell },
  ]

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="bg-white p-8 rounded-lg shadow-xl max-w-md w-full">
          <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">
            AI Financial Assistant
          </h1>
          <LoginForm 
            onLogin={(t) => {
              setToken(t)
              setIsAuthenticated(true)
              localStorage.setItem('token', t)
            }} 
          />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Wallet className="w-6 h-6 text-primary-600" />
              AI Financial Assistant
            </h1>
            <button
              onClick={() => {
                setIsAuthenticated(false)
                setToken(null)
                localStorage.removeItem('token')
              }}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {tab.label}
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'chat' && <ChatInterface token={token} />}
        {activeTab === 'goals' && <GoalsDashboard token={token} />}
        {activeTab === 'insights' && (
          <div className="space-y-6">
            <BudgetInsights token={token} />
            <Recommendations token={token} />
          </div>
        )}
        {activeTab === 'alerts' && <Alerts token={token} />}
      </main>
    </div>
  )
}

function LoginForm({ onLogin }: { onLogin: (token: string) => void }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [isRegister, setIsRegister] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    try {
      const url = `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/v1/auth/${isRegister ? 'register' : 'login'}`
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, username: email.split('@')[0] }),
      })

      const data = await response.json()
      if (response.ok) {
        onLogin(data.access_token || 'demo-token')
      } else {
        setError(data.detail || 'Authentication failed')
      }
    } catch (err) {
      setError('Network error. Please check if the backend is running.')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Email
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Password
        </label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500"
        />
      </div>
      {error && <p className="text-red-600 text-sm">{error}</p>}
      <button
        type="submit"
        className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
      >
        {isRegister ? 'Register' : 'Login'}
      </button>
      <button
        type="button"
        onClick={() => setIsRegister(!isRegister)}
        className="w-full text-sm text-primary-600 hover:text-primary-700"
      >
        {isRegister ? 'Already have an account? Login' : "Don't have an account? Register"}
      </button>
    </form>
  )
}

