import { NextRequest, NextResponse } from 'next/server'

const BOT_API_URL = process.env.NEXT_PUBLIC_BOT_API_URL || 'http://localhost:8000'
const API_KEY = process.env.BOT_API_KEY || 'your-secret-api-key'

// Bot Status abrufen
export async function GET() {
  try {
    const response = await fetch(`${BOT_API_URL}/api/bot/status`)
    const data = await response.json()
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Fehler beim Abrufen des Bot-Status:', error)
    return NextResponse.json(
      { error: 'Fehler beim Abrufen des Bot-Status' },
      { status: 500 }
    )
  }
}

// Bot Kontrolle (Start/Stop)
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action } = body
    
    const response = await fetch(`${BOT_API_URL}/api/bot/control`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${API_KEY}`,
      },
      body: JSON.stringify({ action }),
    })
    
    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.detail || 'Fehler bei Bot-Kontrolle')
    }
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Fehler bei Bot-Kontrolle:', error)
    return NextResponse.json(
      { error: 'Fehler bei Bot-Kontrolle' },
      { status: 500 }
    )
  }
}
