'use client'

import { useState, useEffect } from 'react'
import { TrendingUp, TrendingDown, DollarSign } from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

export default function BudgetInsights({ token }: { token: string | null }) {
  const [insights, setInsights] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchInsights()
  }, [])

  const fetchInsights = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/v1/budgeting/insights`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      )
      if (response.ok) {
        const data = await response.json()
        setInsights(data)
      }
    } catch (error) {
      console.error('Error fetching insights:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return <div className="text-center py-8">Loading insights...</div>
  }

  if (!insights) {
    return <div className="text-center py-8 text-gray-600">No insights available</div>
  }

  const categoryData = Object.entries(insights.category_breakdown || {}).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value: value as number,
  }))

  const COLORS = ['#0ea5e9', '#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#d946ef']

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Budget Insights</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Income</p>
              <p className="text-2xl font-bold text-gray-900">
                ${insights.summary?.total_income?.toLocaleString() || '0'}
              </p>
            </div>
            <TrendingUp className="w-8 h-8 text-blue-600" />
          </div>
        </div>

        <div className="bg-red-50 p-4 rounded-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Expenses</p>
              <p className="text-2xl font-bold text-gray-900">
                ${insights.summary?.total_expenses?.toLocaleString() || '0'}
              </p>
            </div>
            <TrendingDown className="w-8 h-8 text-red-600" />
          </div>
        </div>

        <div className={`p-4 rounded-lg ${(insights.summary?.net || 0) >= 0 ? 'bg-green-50' : 'bg-orange-50'}`}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Net</p>
              <p className={`text-2xl font-bold ${(insights.summary?.net || 0) >= 0 ? 'text-green-600' : 'text-orange-600'}`}>
                ${insights.summary?.net?.toLocaleString() || '0'}
              </p>
            </div>
            <DollarSign className={`w-8 h-8 ${(insights.summary?.net || 0) >= 0 ? 'text-green-600' : 'text-orange-600'}`} />
          </div>
        </div>
      </div>

      {categoryData.length > 0 && (
        <div className="mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Spending by Category</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={categoryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#0ea5e9" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {insights.ai_insights && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Recommendations</h3>
          <p className="text-gray-700 whitespace-pre-wrap">
            {typeof insights.ai_insights === 'string' 
              ? insights.ai_insights 
              : JSON.stringify(insights.ai_insights, null, 2)}
          </p>
        </div>
      )}
    </div>
  )
}

