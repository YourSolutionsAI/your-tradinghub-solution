import { NextRequest, NextResponse } from 'next/server'

const BOT_API_URL = process.env.NEXT_PUBLIC_BOT_API_URL || 'http://localhost:8000'
const API_KEY = process.env.BOT_API_KEY || 'your-secret-api-key'

// Trading Pairs abrufen
export async function GET() {
  try {
    const response = await fetch(`${BOT_API_URL}/api/trading-pairs`)
    const data = await response.json()
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Fehler beim Abrufen der Trading Pairs:', error)
    return NextResponse.json(
      { error: 'Fehler beim Abrufen der Trading Pairs' },
      { status: 500 }
    )
  }
}

// Trading Pairs aktualisieren
export async function PUT(request: NextRequest) {
  try {
    const pairs = await request.json()
    
    const response = await fetch(`${BOT_API_URL}/api/trading-pairs`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`,
      },
      body: JSON.stringify(pairs),
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.detail || 'Fehler beim Aktualisieren der Trading Pairs')
    }
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Fehler beim Aktualisieren der Trading Pairs:', error)
    return NextResponse.json(
      { error: 'Fehler beim Aktualisieren der Trading Pairs' },
      { status: 500 }
    )
  }
}
