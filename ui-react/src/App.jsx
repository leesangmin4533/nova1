import './App.css'

function App() {
  const data = {
    sentiment: '중립',
    decision: 'HOLD',
    reason: '추세 약화로 관망',
    score: 72,
    logs: [
      { time: '10:00', action: 'BUY', reason: '이평선 돌파' },
      { time: '10:05', action: 'HOLD', reason: '거래량 감소' },
      { time: '10:10', action: 'SELL', reason: 'RSI 과매수' }
    ]
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0d1b2a] to-[#1b263b] text-white p-6">
      <div className="max-w-3xl mx-auto space-y-6">
        <h1 className="text-2xl font-bold text-center">NOVA Decision Overview</h1>
        <div className="grid sm:grid-cols-2 gap-4">
          <section className="bg-white/10 p-4 rounded">
            <h2 className="font-semibold mb-1">시장 감정</h2>
            <p className="text-sky-300 text-lg">{data.sentiment}</p>
          </section>
          <section className="bg-white/10 p-4 rounded">
            <h2 className="font-semibold mb-1">NOVA 판단 결과</h2>
            <p className="text-sky-300 text-lg">{data.decision}</p>
          </section>
          <section className="bg-white/10 p-4 rounded sm:col-span-2">
            <h2 className="font-semibold mb-1">판단 이유</h2>
            <p className="text-sky-300">{data.reason}</p>
          </section>
          <section className="bg-white/10 p-4 rounded sm:col-span-2">
            <h2 className="font-semibold mb-1">판단력 점수</h2>
            <p className="text-sky-300 text-xl">{data.score}</p>
          </section>
          <section className="bg-white/10 p-4 rounded sm:col-span-2">
            <h2 className="font-semibold mb-2">최근 판단 로그</h2>
            <ul className="space-y-1 text-sm">
              {data.logs.map((log, idx) => (
                <li key={idx} className="flex justify-between">
                  <span>{log.time}</span>
                  <span className="text-sky-300">{log.action}</span>
                  <span>{log.reason}</span>
                </li>
              ))}
            </ul>
          </section>
        </div>
      </div>
    </div>
  )
}

export default App
