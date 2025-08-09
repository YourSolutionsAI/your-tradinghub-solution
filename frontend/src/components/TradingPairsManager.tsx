'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

interface TradingPairsManagerProps {
  onUpdate: () => void
}

interface TradingPairsData {
  current_pairs: string[]
  available_symbols: string[]
}

export function TradingPairsManager({ onUpdate }: TradingPairsManagerProps) {
  const [data, setData] = useState<TradingPairsData | null>(null)
  const [selectedPairs, setSelectedPairs] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  const fetchTradingPairs = async () => {
    try {
      const response = await fetch('/api/trading-pairs')
      if (!response.ok) throw new Error('Failed to fetch trading pairs')
      const data = await response.json()
      setData(data)
      setSelectedPairs(data.current_pairs)
    } catch (error) {
      console.error('Trading Pairs Fehler:', error)
    } finally {
      setLoading(false)
    }
  }

  const updateTradingPairs = async () => {
    setSaving(true)
    try {
      const response = await fetch('/api/trading-pairs', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pairs: selectedPairs }),
      })

      if (!response.ok) throw new Error('Failed to update trading pairs')
      
      await fetchTradingPairs()
      onUpdate()
    } catch (error) {
      console.error('Update Fehler:', error)
    } finally {
      setSaving(false)
    }
  }

  const togglePair = (pair: string) => {
    setSelectedPairs(prev => 
      prev.includes(pair) 
        ? prev.filter(p => p !== pair)
        : [...prev, pair]
    )
  }

  useEffect(() => {
    fetchTradingPairs()
  }, [])

  if (loading) {
    return (
      <Card className="bg-gray-800 border-gray-700">
        <CardContent className="p-6">
          <div className="text-center">Loading...</div>
        </CardContent>
      </Card>
    )
  }

  const popularPairs = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 'XRPUSDT', 'DOTUSDT', 'LINKUSDT']

  return (
    <Card className="bg-gray-800 border-gray-700">
      <CardHeader>
        <CardTitle className="text-white">Trading Pairs Management</CardTitle>
        <CardDescription>
          Wähle die Kryptowährungen für automatisches Trading
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Current Pairs */}
        <div>
          <h3 className="text-lg font-semibold mb-3">📈 Aktive Trading Pairs</h3>
          <div className="flex flex-wrap gap-2">
            {data?.current_pairs.map(pair => (
              <Badge key={pair} className="bg-green-600 text-white">
                {pair}
              </Badge>
            )) || <span className="text-gray-400">Keine aktiven Pairs</span>}
          </div>
        </div>

        {/* Popular Pairs Selection */}
        <div>
          <h3 className="text-lg font-semibold mb-3">🔥 Beliebte Trading Pairs</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            {popularPairs.map(pair => (
              <Button
                key={pair}
                variant={selectedPairs.includes(pair) ? "default" : "outline"}
                size="sm"
                onClick={() => togglePair(pair)}
                className={selectedPairs.includes(pair) 
                  ? "bg-blue-600 hover:bg-blue-700 text-white" 
                  : "text-gray-300 border-gray-600 hover:bg-gray-700"
                }
              >
                {pair}
              </Button>
            ))}
          </div>
        </div>

        {/* Selected Pairs Preview */}
        <div>
          <h3 className="text-lg font-semibold mb-3">✅ Ausgewählte Pairs ({selectedPairs.length})</h3>
          <div className="flex flex-wrap gap-2 mb-4">
            {selectedPairs.map(pair => (
              <Badge key={pair} variant="secondary" className="bg-blue-600">
                {pair}
                <button 
                  onClick={() => togglePair(pair)}
                  className="ml-2 text-xs hover:text-red-300"
                >
                  ×
                </button>
              </Badge>
            ))}
            {selectedPairs.length === 0 && (
              <span className="text-gray-400">Keine Pairs ausgewählt</span>
            )}
          </div>
        </div>

        {/* Save Button */}
        <div className="flex justify-end space-x-2">
          <Button
            onClick={() => setSelectedPairs(data?.current_pairs || [])}
            variant="outline"
            className="text-gray-300 border-gray-600"
          >
            Reset
          </Button>
          <Button
            onClick={updateTradingPairs}
            disabled={saving || selectedPairs.length === 0}
            className="bg-green-600 hover:bg-green-700"
          >
            {saving ? 'Speichere...' : 'Trading Pairs Aktivieren'}
          </Button>
        </div>

        {/* Info */}
        <div className="bg-gray-700 p-4 rounded-lg">
          <p className="text-sm text-gray-300">
            💡 <strong>Tipp:</strong> Starte mit 2-3 stabilen Pairs wie BTC/ETH. 
            Der Bot verwendet eine Moving Average Strategie mit 5% Risiko pro Trade.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
