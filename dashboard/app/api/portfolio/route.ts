import { NextResponse } from 'next/server'

const BOT_API_URL = process.env.NEXT_PUBLIC_BOT_API_URL || 'http://localhost:8000'

export async function GET() {
  try {
    const response = await fetch(`${BOT_API_URL}/api/portfolio`)
    const data = await response.json()
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Fehler beim Abrufen des Portfolios:', error)
    return NextResponse.json(
      { error: 'Fehler beim Abrufen des Portfolios' },
      { status: 500 }
    )
  }
}
