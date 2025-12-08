'use client'

import { useState, useEffect } from 'react'
import { Bell, AlertCircle, CheckCircle, Plus } from 'lucide-react'

interface Alert {
  id: number
  alert_type: string
  title: string
  message: string
  priority: string
  is_read: boolean
  created_at: string
  alert_metadata?: string | null
}

export default function Alerts({ token }: { token: string | null }) {
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showObligationForm, setShowObligationForm] = useState(false)
  const [obligationForm, setObligationForm] = useState({
    title: '',
    obligation_type: 'credit_card_bill',
    amount: '',
    due_date: '',
    frequency: 'monthly',
    provider: '',
  })

  useEffect(() => {
    fetchAlerts()
  }, [])

  const fetchAlerts = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/v1/alerts?is_read=false`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      )
      if (response.ok) {
        const data = await response.json()
        setAlerts(data)
      }
    } catch (error) {
      console.error('Error fetching alerts:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const markAsRead = async (alertId: number) => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/v1/alerts/${alertId}/read`,
        {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        }
      )
      if (response.ok) {
        setAlerts(alerts.filter(a => a.id !== alertId))
      }
    } catch (error) {
      console.error('Error marking alert as read:', error)
    }
  }

  const generateAlerts = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/v1/alerts/generate`,
        {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        }
      )
      if (response.ok) {
        fetchAlerts()
      }
    } catch (error) {
      console.error('Error generating alerts:', error)
    }
  }

  const createObligation = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}/api/v1/obligations`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            ...obligationForm,
            amount: parseFloat(obligationForm.amount),
            due_date: new Date(obligationForm.due_date).toISOString(),
          }),
        }
      )
      if (response.ok) {
        setShowObligationForm(false)
        setObligationForm({
          title: '',
          obligation_type: 'credit_card_bill',
          amount: '',
          due_date: '',
          frequency: 'monthly',
          provider: '',
        })
        generateAlerts()
      }
    } catch (error) {
      console.error('Error creating obligation:', error)
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 border-red-500 text-red-800'
      case 'high':
        return 'bg-orange-100 border-orange-500 text-orange-800'
      case 'medium':
        return 'bg-yellow-100 border-yellow-500 text-yellow-800'
      default:
        return 'bg-blue-100 border-blue-500 text-blue-800'
    }
  }

  if (isLoading) {
    return <div className="text-center py-8">Loading alerts...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Bell className="w-6 h-6 text-primary-600" />
          Financial Alerts
        </h2>
        <button
          onClick={generateAlerts}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
        >
          Generate Alerts
        </button>
      </div>

      <button
        onClick={() => setShowObligationForm(!showObligationForm)}
        className="flex items-center gap-2 text-primary-700 bg-primary-50 border border-primary-200 px-3 py-2 rounded"
      >
        <Plus className="w-4 h-4" />
        Add recurring payment (card bill/EMI/SIP/insurance)
      </button>

      {showObligationForm && (
        <div className="bg-white border rounded-lg p-4 shadow-sm">
          <form onSubmit={createObligation} className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
              <input
                type="text"
                value={obligationForm.title}
                onChange={(e) => setObligationForm({ ...obligationForm, title: e.target.value })}
                required
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <select
                value={obligationForm.obligation_type}
                onChange={(e) => setObligationForm({ ...obligationForm, obligation_type: e.target.value })}
                className="w-full px-3 py-2 border rounded"
              >
                <option value="credit_card_bill">Credit Card Bill</option>
                <option value="emi">EMI</option>
                <option value="sip">SIP</option>
                <option value="insurance">Insurance</option>
                <option value="utility">Utility</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Provider</label>
              <input
                type="text"
                value={obligationForm.provider}
                onChange={(e) => setObligationForm({ ...obligationForm, provider: e.target.value })}
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Amount</label>
              <input
                type="number"
                value={obligationForm.amount}
                onChange={(e) => setObligationForm({ ...obligationForm, amount: e.target.value })}
                required
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
              <input
                type="date"
                value={obligationForm.due_date}
                onChange={(e) => setObligationForm({ ...obligationForm, due_date: e.target.value })}
                required
                className="w-full px-3 py-2 border rounded"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Frequency</label>
              <select
                value={obligationForm.frequency}
                onChange={(e) => setObligationForm({ ...obligationForm, frequency: e.target.value })}
                className="w-full px-3 py-2 border rounded"
              >
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="yearly">Yearly</option>
                <option value="weekly">Weekly</option>
                <option value="one_time">One-time</option>
              </select>
            </div>
            <div className="col-span-2 flex gap-2">
              <button
                type="submit"
                className="bg-primary-600 text-white px-4 py-2 rounded hover:bg-primary-700"
              >
                Save
              </button>
              <button
                type="button"
                onClick={() => setShowObligationForm(false)}
                className="px-4 py-2 border rounded"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="space-y-4">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className={`border-l-4 p-4 rounded-r-lg ${getPriorityColor(alert.priority)}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <AlertCircle className="w-5 h-5" />
                  <h3 className="font-semibold">{alert.title}</h3>
                  <span className="text-xs bg-white/50 px-2 py-1 rounded capitalize">
                    {alert.priority}
                  </span>
                </div>
                <p className="text-sm mb-2">{alert.message}</p>
                <p className="text-xs opacity-75">
                  {new Date(alert.created_at).toLocaleString()}
                </p>
                {alert.alert_metadata && (
                  <p className="text-xs opacity-75 mt-1">
                    {(() => {
                      try {
                        const meta = JSON.parse(alert.alert_metadata)
                        if (meta.due_date) {
                          return `Due: ${new Date(meta.due_date).toLocaleDateString()}`
                        }
                      } catch (e) {
                        return null
                      }
                    })()}
                  </p>
                )}
              </div>
              <button
                onClick={() => markAsRead(alert.id)}
                className="ml-4 text-sm hover:underline flex items-center gap-1"
              >
                <CheckCircle className="w-4 h-4" />
                Mark as read
              </button>
            </div>
          </div>
        ))}
      </div>

      {alerts.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <Bell className="w-16 h-16 mx-auto text-gray-300 mb-4" />
          <p className="text-gray-600">No active alerts</p>
          <p className="text-sm text-gray-500 mt-2">Click "Generate Alerts" to check for new notifications</p>
        </div>
      )}
    </div>
  )
}

