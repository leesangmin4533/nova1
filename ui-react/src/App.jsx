import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [status, setStatus] = useState(null)

  useEffect(() => {
    async function fetchStatus() {
      try {
        const res = await fetch('/api/status')
        const data = await res.json()
        setStatus(data)
      } catch (err) {
        console.error('Failed to fetch status', err)
      }
    }
    fetchStatus()
    const id = setInterval(fetchStatus, 5000)
    return () => clearInterval(id)
  }, [])

  if (!status) {
    return <div className="p-4 text-center">Loading...</div>
  }

  const decision = status.decision || {}

  return (
    <div className="min-h-screen bg-gray-900 text-white p-4 space-y-4">
      <h1 className="text-2xl font-bold">NOVA Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <section className="bg-gray-800 p-4 rounded">
          <h2 className="text-xl font-semibold mb-2">Market Sentiment</h2>
          <p className="text-3xl">{status.sentiment}</p>
        </section>
        <section className="bg-gray-800 p-4 rounded">
          <h2 className="text-xl font-semibold mb-2">Strategy</h2>
          <p>{status.selected_strategy}</p>
          <p className="text-sm text-gray-400">Score: {status.strategy_score}</p>
        </section>
        <section className="bg-gray-800 p-4 rounded">
          <h2 className="text-xl font-semibold mb-2">Position</h2>
          <p>Price: {status.price}</p>
          <p>Equity: {status.equity}</p>
        </section>
        <section className="bg-gray-800 p-4 rounded">
          <h2 className="text-xl font-semibold mb-2">Last Decision</h2>
          <p>Action: {decision.action}</p>
          <p>Reason: {decision.reason}</p>
        </section>
      </div>
    </div>
  )
}

export default App
