'use client'

import { useState, useEffect } from 'react'
import { Sparkles, TrendingUp } from 'lucide-react'

interface Recommendation {
  product: {
    id: number
    name: string
    product_type: string
    risk_level: string
    expected_return: number
    min_investment: number
    issuer?: string
    annual_fee?: number
    rewards_type?: string
    welcome_bonus?: string
    intro_apr_months?: number
  }
  match_score: number
  reasoning: string
  suitability_factors: string[]
  recommended_investment: number
}

export default function Recommendations({ token }: { token: string | null }) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    fetchRecommendations()
  }, [])

  const fetchRecommendations = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/v1/recommendations?limit=5`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      )
      if (response.ok) {
        const data = await response.json()
        setRecommendations(data)
      }
    } catch (error) {
      console.error('Error fetching recommendations:', error)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return <div className="text-center py-8">Loading recommendations...</div>
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center gap-2 mb-6">
        <Sparkles className="w-6 h-6 text-primary-600" />
        <h2 className="text-2xl font-bold text-gray-900">Product Recommendations</h2>
      </div>

      <div className="space-y-6">
        {recommendations.map((rec, idx) => (
          <div key={idx} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{rec.product.name}</h3>
                <p className="text-sm text-gray-600 capitalize">{rec.product.product_type.replace('_', ' ')}</p>
              </div>
              <div className="text-right">
                <div className="text-sm text-gray-600">Match Score</div>
                <div className="text-2xl font-bold text-primary-600">
                  {(rec.match_score * 100).toFixed(0)}%
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-600">Risk Level</p>
                <p className="font-medium capitalize">{rec.product.risk_level}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Expected Return</p>
                <p className="font-medium">{rec.product.expected_return}% p.a.</p>
              </div>
              {rec.product.issuer && (
                <div>
                  <p className="text-sm text-gray-600">Issuer</p>
                  <p className="font-medium">{rec.product.issuer}</p>
                </div>
              )}
              {rec.product.annual_fee !== undefined && (
                <div>
                  <p className="text-sm text-gray-600">Annual Fee</p>
                  <p className="font-medium">${rec.product.annual_fee?.toLocaleString()}</p>
                </div>
              )}
              {rec.product.rewards_type && (
                <div className="col-span-2">
                  <p className="text-sm text-gray-600">Rewards</p>
                  <p className="font-medium capitalize">{rec.product.rewards_type}</p>
                </div>
              )}
              {rec.product.welcome_bonus && (
                <div className="col-span-2">
                  <p className="text-sm text-gray-600">Welcome Bonus</p>
                  <p className="font-medium">{rec.product.welcome_bonus}</p>
                </div>
              )}
            </div>

            <div className="mb-4">
              <p className="text-sm font-medium text-gray-900 mb-2">Why this product?</p>
              <p className="text-sm text-gray-700 bg-gray-50 p-3 rounded">{rec.reasoning}</p>
            </div>

            {rec.suitability_factors && rec.suitability_factors.length > 0 && (
              <div className="mb-4">
                <p className="text-sm font-medium text-gray-900 mb-2">Suitability Factors:</p>
                <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                  {rec.suitability_factors.map((factor, i) => (
                    <li key={i}>{factor}</li>
                  ))}
                </ul>
              </div>
            )}

            {rec.recommended_investment && (
              <div className="flex items-center justify-between pt-4 border-t">
                <span className="text-sm text-gray-600">Recommended Investment</span>
                <span className="text-lg font-bold text-primary-600">
                  ${rec.recommended_investment.toLocaleString()}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>

      {recommendations.length === 0 && (
        <div className="text-center py-12">
          <TrendingUp className="w-16 h-16 mx-auto text-gray-300 mb-4" />
          <p className="text-gray-600">No recommendations available at the moment</p>
        </div>
      )}
    </div>
  )
}

