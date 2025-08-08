'use client'

import { useEffect, useState } from 'react'
import { createClientComponentClient } from '@supabase/auth-helpers-nextjs'
import { 
  ArrowUpIcon, 
  ArrowDownIcon, 
  PlayIcon, 
  PauseIcon,
  CpuChipIcon,
  CurrencyDollarIcon,
  ChartBarIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import toast from 'react-hot-toast'

interface BotStatus {
  status: string
  last_heartbeat: string
  timestamp: string
}

interface Portfolio {
  total_balance_usdt: number
  assets: Array<{
    asset: string
    balance: number
  }>
}

interface Trade {
  id: string
  side: string
  symbol: string
  amount: number
  timestamp: string
  status: string
}

interface MarketData {
  symbol: string
  price: number
  price_change_24h: number
  volume_24h: number
  timestamp: string
}

export default function Dashboard() {
  const [botStatus, setBotStatus] = useState<BotStatus | null>(null)
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null)
  const [recentTrades, setRecentTrades] = useState<Trade[]>([])
  const [marketData, setMarketData] = useState<MarketData[]>([])
  const [priceHistory, setPriceHistory] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  const supabase = createClientComponentClient()

  useEffect(() => {
    fetchDashboardData()
    
    // Daten alle 30 Sekunden aktualisieren
    const interval = setInterval(fetchDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Bot Status abrufen
      const { data: statusData } = await supabase
        .from('bot_status')
        .select('*')
        .order('timestamp', { ascending: false })
        .limit(1)
        .single()

      if (statusData) setBotStatus(statusData)

      // Portfolio abrufen
      const { data: portfolioData } = await supabase
        .from('portfolio_snapshots')
        .select('*')
        .order('timestamp', { ascending: false })
        .limit(1)
        .single()

      if (portfolioData) setPortfolio(portfolioData)

      // Letzte Trades abrufen
      const { data: tradesData } = await supabase
        .from('trades')
        .select('*')
        .order('timestamp', { ascending: false })
        .limit(10)

      if (tradesData) setRecentTrades(tradesData)

      // Aktuelle Marktdaten abrufen
      const { data: marketDataResponse } = await supabase
        .from('market_data')
        .select('*')
        .order('timestamp', { ascending: false })
        .limit(3)

      if (marketDataResponse) setMarketData(marketDataResponse)

      // Preisverlauf für Chart abrufen (letzte 24h)
      const { data: priceHistoryData } = await supabase
        .from('market_data')
        .select('symbol, price, timestamp')
        .eq('symbol', 'BTCUSDT')
        .gte('timestamp', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString())
        .order('timestamp', { ascending: true })

      if (priceHistoryData) {
        const formattedData = priceHistoryData.map(item => ({
          time: new Date(item.timestamp).toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' }),
          price: item.price
        }))
        setPriceHistory(formattedData)
      }

      setLoading(false)
    } catch (error) {
      console.error('Fehler beim Laden der Dashboard-Daten:', error)
      toast.error('Fehler beim Laden der Daten')
    }
  }

  const toggleBot = async () => {
    try {
      const newStatus = botStatus?.status === 'running' ? 'stopped' : 'running'
      
      // Hier würde normalerweise ein API-Call an den Bot gemacht
      toast.success(`Bot ${newStatus === 'running' ? 'gestartet' : 'gestoppt'}`)
      
      // Status lokal aktualisieren (in echter Implementierung vom Bot)
      if (botStatus) {
        setBotStatus({
          ...botStatus,
          status: newStatus,
          timestamp: new Date().toISOString()
        })
      }
    } catch (error) {
      toast.error('Fehler beim Ändern des Bot-Status')
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Trading Bot Dashboard</h1>
        <p className="text-gray-600">Überwachen Sie Ihren Binance Trading Bot in Echtzeit</p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Bot Status */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Bot Status</p>
              <p className={`text-lg font-semibold ${
                botStatus?.status === 'running' ? 'text-success-600' : 'text-danger-600'
              }`}>
                {botStatus?.status === 'running' ? 'Aktiv' : 'Inaktiv'}
              </p>
            </div>
            <CpuChipIcon className={`h-8 w-8 ${
              botStatus?.status === 'running' ? 'text-success-600' : 'text-gray-400'
            }`} />
          </div>
          <button
            onClick={toggleBot}
            className={`mt-4 w-full flex items-center justify-center gap-2 ${
              botStatus?.status === 'running' ? 'btn-danger' : 'btn-success'
            }`}
          >
            {botStatus?.status === 'running' ? (
              <>
                <PauseIcon className="h-4 w-4" />
                Bot stoppen
              </>
            ) : (
              <>
                <PlayIcon className="h-4 w-4" />
                Bot starten
              </>
            )}
          </button>
        </div>

        {/* Portfolio Wert */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Portfolio Wert</p>
              <p className="text-lg font-semibold text-gray-900">
                ${portfolio?.total_balance_usdt?.toFixed(2) || '0.00'}
              </p>
            </div>
            <CurrencyDollarIcon className="h-8 w-8 text-primary-600" />
          </div>
        </div>

        {/* Anzahl Trades heute */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Trades heute</p>
              <p className="text-lg font-semibold text-gray-900">
                {recentTrades.filter(trade => 
                  new Date(trade.timestamp).toDateString() === new Date().toDateString()
                ).length}
              </p>
            </div>
            <ChartBarIcon className="h-8 w-8 text-primary-600" />
          </div>
        </div>

        {/* Letzter Heartbeat */}
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Letzter Heartbeat</p>
              <p className="text-sm text-gray-900">
                {botStatus?.last_heartbeat ? 
                  new Date(botStatus.last_heartbeat).toLocaleTimeString('de-DE') : 
                  'Keine Daten'
                }
              </p>
            </div>
            <ClockIcon className="h-8 w-8 text-gray-400" />
          </div>
        </div>
      </div>

      {/* Charts und Tabellen */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Preisverlauf Chart */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">BTC/USDT Preisverlauf (24h)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={priceHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="price" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Aktuelle Marktdaten */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Marktdaten</h3>
          <div className="space-y-4">
            {marketData.map((data) => (
              <div key={data.symbol} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{data.symbol}</p>
                  <p className="text-sm text-gray-600">${data.price.toFixed(2)}</p>
                </div>
                <div className={`flex items-center gap-1 ${
                  data.price_change_24h >= 0 ? 'text-success-600' : 'text-danger-600'
                }`}>
                  {data.price_change_24h >= 0 ? (
                    <ArrowUpIcon className="h-4 w-4" />
                  ) : (
                    <ArrowDownIcon className="h-4 w-4" />
                  )}
                  <span className="font-medium">{Math.abs(data.price_change_24h).toFixed(2)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Letzte Trades */}
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Letzte Trades</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Zeit
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Typ
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Symbol
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Menge
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentTrades.map((trade) => (
                <tr key={trade.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {new Date(trade.timestamp).toLocaleString('de-DE')}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                      trade.side === 'BUY' 
                        ? 'bg-success-100 text-success-800' 
                        : 'bg-danger-100 text-danger-800'
                    }`}>
                      {trade.side}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {trade.symbol}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {trade.amount.toFixed(6)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-gray-100 text-gray-800">
                      {trade.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
