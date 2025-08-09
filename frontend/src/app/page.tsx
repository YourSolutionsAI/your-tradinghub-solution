'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { TradingPairsManager } from '@/components/TradingPairsManager'
import { PortfolioView } from '@/components/PortfolioView'
import { MarketDataView } from '@/components/MarketDataView'

interface BotStatus {
  status: string
  is_trading: boolean
  trading_pairs: string[]
  last_check: string | null
}

export default function TradingDashboard() {
  const [botStatus, setBotStatus] = useState<BotStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchBotStatus = async () => {
    try {
      const response = await fetch('/api/bot/status')
      if (!response.ok) throw new Error('Failed to fetch bot status')
      const data = await response.json()
      setBotStatus(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const controlBot = async (action: 'start' | 'stop') => {
    try {
      const response = await fetch('/api/bot/control', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ action }),
      })

      if (!response.ok) throw new Error(`Failed to ${action} bot`)
      
      await fetchBotStatus()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    }
  }

  useEffect(() => {
    fetchBotStatus()
    const interval = setInterval(fetchBotStatus, 5000) // Update every 5 seconds
    return () => clearInterval(interval)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center">
        <div className="text-xl">Loading Trading Dashboard...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">🚀 Live Trading Dashboard</h1>
          <p className="text-gray-400">Professional Binance Trading Bot Control Center</p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert className="mb-6 border-red-500 bg-red-500/10">
            <AlertDescription className="text-red-400">{error}</AlertDescription>
          </Alert>
        )}

        {/* Bot Status Card */}
        <Card className="mb-6 bg-gray-800 border-gray-700">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-white">Bot Status</CardTitle>
                <CardDescription>
                  Live Trading Bot Control
                </CardDescription>
              </div>
              <div className="flex items-center space-x-3">
                <Badge 
                  variant={botStatus?.is_trading ? "default" : "secondary"}
                  className={botStatus?.is_trading ? "bg-green-600" : "bg-gray-600"}
                >
                  {botStatus?.is_trading ? "🟢 TRADING" : "🔴 STOPPED"}
                </Badge>
                {botStatus?.is_trading ? (
                  <Button 
                    onClick={() => controlBot('stop')}
                    variant="destructive"
                    size="sm"
                  >
                    Stop Trading
                  </Button>
                ) : (
                  <Button 
                    onClick={() => controlBot('start')}
                    className="bg-green-600 hover:bg-green-700"
                    size="sm"
                  >
                    Start Trading
                  </Button>
                )}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-400">Status</p>
                <p className="font-semibold">{botStatus?.status || 'Unknown'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Trading Pairs</p>
                <p className="font-semibold">{botStatus?.trading_pairs?.length || 0}</p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Last Check</p>
                <p className="font-semibold text-sm">
                  {botStatus?.last_check ? new Date(botStatus.last_check).toLocaleTimeString() : 'Never'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-400">Mode</p>
                <p className="font-semibold text-green-400">LIVE TRADING</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Tabs */}
        <Tabs defaultValue="portfolio" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-gray-800">
            <TabsTrigger value="portfolio">Portfolio</TabsTrigger>
            <TabsTrigger value="trading-pairs">Trading Pairs</TabsTrigger>
            <TabsTrigger value="market">Market Data</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="portfolio" className="space-y-6">
            <PortfolioView />
          </TabsContent>

          <TabsContent value="trading-pairs" className="space-y-6">
            <TradingPairsManager onUpdate={fetchBotStatus} />
          </TabsContent>

          <TabsContent value="market" className="space-y-6">
            <MarketDataView tradingPairs={botStatus?.trading_pairs || []} />
          </TabsContent>

          <TabsContent value="settings" className="space-y-6">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Bot Configuration</CardTitle>
                <CardDescription>
                  Trading bot settings and preferences
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Security</h3>
                    <p className="text-gray-400 text-sm">
                      ✅ Binance Live API Connected<br/>
                      ✅ Secure API Key Authentication<br/>
                      ✅ HTTPS Encrypted Communication
                    </p>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold mb-2">Trading Strategy</h3>
                    <p className="text-gray-400 text-sm">
                      📈 Simple Moving Average (MA10/MA20)<br/>
                      💰 Risk Management: 5% per trade<br/>
                      ⏱️ Check Interval: 30 seconds
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}