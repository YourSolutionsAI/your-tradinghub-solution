'use client'

import { useState, useEffect } from 'react'
import { PlusIcon, TrashIcon, CogIcon } from '@heroicons/react/24/outline'
import toast from 'react-hot-toast'

interface TradingPairsManagerProps {
  onUpdate?: () => void
}

export default function TradingPairsManager({ onUpdate }: TradingPairsManagerProps) {
  const [currentPairs, setCurrentPairs] = useState<string[]>([])
  const [availableSymbols, setAvailableSymbols] = useState<string[]>([])
  const [selectedSymbol, setSelectedSymbol] = useState<string>('')
  const [loading, setLoading] = useState(false)
  const [isOpen, setIsOpen] = useState(false)

  useEffect(() => {
    if (isOpen) {
      fetchTradingPairs()
    }
  }, [isOpen])

  const fetchTradingPairs = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/trading-pairs')
      const data = await response.json()
      
      setCurrentPairs(data.current_pairs || [])
      setAvailableSymbols(data.available_symbols || [])
    } catch (error) {
      console.error('Fehler beim Laden der Trading Pairs:', error)
      toast.error('Fehler beim Laden der Trading Pairs')
    } finally {
      setLoading(false)
    }
  }

  const addTradingPair = async () => {
    if (!selectedSymbol) {
      toast.error('Bitte wählen Sie ein Trading Pair aus')
      return
    }

    if (currentPairs.includes(selectedSymbol)) {
      toast.error('Trading Pair bereits vorhanden')
      return
    }

    const newPairs = [...currentPairs, selectedSymbol]
    await updateTradingPairs(newPairs)
  }

  const removeTradingPair = async (symbol: string) => {
    if (currentPairs.length <= 1) {
      toast.error('Mindestens ein Trading Pair muss vorhanden sein')
      return
    }

    const newPairs = currentPairs.filter(pair => pair !== symbol)
    await updateTradingPairs(newPairs)
  }

  const updateTradingPairs = async (newPairs: string[]) => {
    try {
      setLoading(true)
      
      const response = await fetch('/api/trading-pairs', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newPairs),
      })

      if (!response.ok) {
        throw new Error('Fehler beim Aktualisieren der Trading Pairs')
      }

      setCurrentPairs(newPairs)
      setSelectedSymbol('')
      toast.success('Trading Pairs erfolgreich aktualisiert!')
      
      if (onUpdate) {
        onUpdate()
      }
    } catch (error) {
      console.error('Fehler beim Aktualisieren:', error)
      toast.error('Fehler beim Aktualisieren der Trading Pairs')
    } finally {
      setLoading(false)
    }
  }

  const quickPresets = [
    {
      name: 'Große Coins (Sicher)',
      pairs: ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
    },
    {
      name: 'Altcoins (Riskant)',
      pairs: ['SOLUSDT', 'ADAUSDT', 'DOGEUSDT', 'XRPUSDT']
    },
    {
      name: 'DeFi Tokens',
      pairs: ['UNIUSDT', 'AAVEUSDT', 'LINKUSDT', 'COMPUSDT']
    },
    {
      name: 'Meme Coins (Sehr Riskant)',
      pairs: ['DOGEUSDT', 'SHIBUSDT', 'PEPEUSDT']
    }
  ]

  const applyPreset = async (preset: typeof quickPresets[0]) => {
    await updateTradingPairs(preset.pairs)
  }

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="btn-primary flex items-center gap-2"
      >
        <CogIcon className="h-4 w-4" />
        Trading Pairs verwalten
      </button>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto mx-4">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Trading Pairs verwalten</h2>
          <button
            onClick={() => setIsOpen(false)}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>

        {/* Aktuelle Trading Pairs */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Aktuelle Trading Pairs ({currentPairs.length})
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2">
            {currentPairs.map((pair) => (
              <div
                key={pair}
                className="flex items-center justify-between bg-gray-100 rounded-lg p-3"
              >
                <span className="font-medium text-gray-900">{pair}</span>
                <button
                  onClick={() => removeTradingPair(pair)}
                  className="text-red-500 hover:text-red-700"
                  disabled={loading || currentPairs.length <= 1}
                >
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Neues Trading Pair hinzufügen */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Neues Trading Pair hinzufügen
          </h3>
          <div className="flex gap-2">
            <select
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
              className="flex-1 rounded-md border border-gray-300 px-3 py-2"
              disabled={loading}
            >
              <option value="">Trading Pair auswählen...</option>
              {availableSymbols
                .filter(symbol => !currentPairs.includes(symbol))
                .map((symbol) => (
                  <option key={symbol} value={symbol}>
                    {symbol}
                  </option>
                ))}
            </select>
            <button
              onClick={addTradingPair}
              disabled={loading || !selectedSymbol}
              className="btn-primary flex items-center gap-2"
            >
              <PlusIcon className="h-4 w-4" />
              Hinzufügen
            </button>
          </div>
        </div>

        {/* Schnell-Presets */}
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Schnell-Presets
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {quickPresets.map((preset) => (
              <button
                key={preset.name}
                onClick={() => applyPreset(preset)}
                disabled={loading}
                className="text-left p-4 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="font-medium text-gray-900 mb-1">
                  {preset.name}
                </div>
                <div className="text-sm text-gray-600">
                  {preset.pairs.join(', ')}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Schließen Button */}
        <div className="flex justify-end">
          <button
            onClick={() => setIsOpen(false)}
            className="btn-secondary"
          >
            Schließen
          </button>
        </div>

        {loading && (
          <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        )}
      </div>
    </div>
  )
}
