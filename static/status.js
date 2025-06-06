// UTC → 한국 시간 변환 함수
function formatToKST(utcTimestamp) {
    const date = new Date(utcTimestamp);
    const kstDate = new Date(date.getTime() + 9 * 60 * 60 * 1000);
    return kstDate.toLocaleString("ko-KR", { hour12: false, timeZone: "Asia/Seoul" });
}

// 포지션 수익률 갱신
function updateReturnTable(positions, currentPrice) {
    const body = document.querySelector('#returnTable tbody');
    body.innerHTML = '';

    positions.forEach(pos => {
        const rate = ((currentPrice - pos.entry_price) / pos.entry_price * 100).toFixed(2);
        const row = document.createElement('tr');
        row.innerHTML = `
          <td>${pos.symbol}</td>
          <td>${pos.entry_price}</td>
          <td>${currentPrice}</td>
          <td style="color:${rate >= 0 ? 'green' : 'red'}">${rate}%</td>
        `;
        body.appendChild(row);
    });
}

async function refresh() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        document.getElementById('sentiment').innerText = data.sentiment || '-';
        document.getElementById('strategy').innerText = data.strategy || '-';
        if (data.selected_strategy) {
            const prob = (data.strategy_score * 100).toFixed(2);
            document.getElementById('selected_strategy').innerText = `${data.selected_strategy} (${prob}%)`;
        } else {
            document.getElementById('selected_strategy').innerText = '-';
        }
        document.getElementById('signal').innerText = data.signal || '-';
        document.getElementById('price').innerText = (data.price !== null && data.price !== undefined) ? data.price.toFixed(2) : '-';
        document.getElementById('balance').innerText = (data.balance !== null && data.balance !== undefined) ? data.balance.toFixed(2) : '-';
        if (data.position && data.position.entry_price !== undefined) {
            const rr = (data.position.return_rate * 100).toFixed(2);
            document.getElementById('position').innerText = `${data.position.entry_price} (${rr}%)`;
        } else {
            document.getElementById('position').innerText = '-';
        }
        document.getElementById('weight').innerText = (data.weight !== undefined && data.weight !== null) ? data.weight.toFixed(2) : '-';
        document.getElementById('rsi').innerText = (data.rsi !== undefined && data.rsi !== null) ? data.rsi.toFixed(2) : '-';
        document.getElementById('bb_score').innerText = data.bb_score !== undefined ? data.bb_score : '-';
        document.getElementById('ts_score').innerText = data.ts_score !== undefined ? data.ts_score : '-';
        if (data.nearest_failed) {
            const nf = data.nearest_failed;
            const text = `${nf.condition} (${nf.diff.toFixed(2)})`;
            const elem = document.getElementById('nearest_failed');
            elem.innerText = text;
            elem.classList.toggle('negative', nf.diff < 0);
        } else {
            document.getElementById('nearest_failed').innerText = '-';
        }
        if (data.return_rate !== null && data.return_rate !== undefined) {
            const elem = document.getElementById('return_rate');
            const val = (data.return_rate * 100).toFixed(2);
            elem.innerText = val + '%';
            elem.classList.toggle('positive', data.return_rate > 0);
            elem.classList.toggle('negative', data.return_rate < 0);
        } else {
            document.getElementById('return_rate').innerText = '-';
        }
        if (data.last_trade_time) {
            const t = new Date(data.last_trade_time);
            const kst = new Date(t.getTime() + 9 * 60 * 60 * 1000);
            const s = kst.toISOString().replace('T', ' ').substring(0, 19);
            document.getElementById('last_trade_time').innerText = s;
        } else {
            document.getElementById('last_trade_time').innerText = '-';
        }
        if (data.cumulative_return !== null && data.cumulative_return !== undefined) {
            const elem = document.getElementById('cumulative_return');
            const val = (data.cumulative_return * 100).toFixed(2);
            elem.innerText = val + '%';
            elem.classList.toggle('positive', data.cumulative_return > 0);
            elem.classList.toggle('negative', data.cumulative_return < 0);
        } else {
            document.getElementById('cumulative_return').innerText = '-';
        }

        if (data.weights && Object.keys(data.weights).length > 0) {
            const labels = Object.keys(data.weights);
            const values = labels.map(k => data.weights[k]);
            const trace = {x: labels, y: values, type: 'bar'};
            Plotly.react('weights_chart', [trace], {margin: {t: 20}});
        }

        // 매수/매도 횟수 표시
        document.getElementById('buyCount').textContent = data.buy_count || 0;
        document.getElementById('sellCount').textContent = data.sell_count || 0;

        // 거래 내역 표시
        const tradeList = document.getElementById('tradeList');
        tradeList.innerHTML = '';
        if (data.recent_trades) {
            data.recent_trades.slice(-10).forEach(trade => {
                const item = document.createElement('li');
                item.textContent = `${formatToKST(trade.timestamp)} - ${trade.action} @ ${trade.price}`;
                item.classList.add('trade-entry');
                if (trade.action === 'BUY') item.classList.add('buy-highlight');
                if (trade.action === 'SELL') item.classList.add('sell-highlight');
                tradeList.appendChild(item);
            });
        }

        // 포지션별 수익률 테이블 갱신
        if (data.positions && data.positions.length > 0 && data.price !== undefined) {
            updateReturnTable(data.positions, data.price);
        } else {
            const body = document.querySelector('#returnTable tbody');
            if (body) body.innerHTML = '';
        }

        if (data.bid_volume !== null && data.ask_volume !== null) {
            const total = data.bid_volume + data.ask_volume;
            const ratio = total ? ((data.bid_volume - data.ask_volume) / total) : 0;
            document.getElementById('selected_strategy').title = `호가 점수: ${ratio.toFixed(2)}`;
            document.getElementById('orderbook_ratio').innerText = ratio.toFixed(2);
            document.getElementById('orderbook_ratio').classList.toggle('positive', ratio > 0);
            document.getElementById('orderbook_ratio').classList.toggle('negative', ratio < 0);
        }

        // 📈 실시간 시세 그래프
        if (!window.priceHistory) window.priceHistory = [];
        const now = new Date();
        window.priceHistory.push({ x: now, y: data.price });
        if (window.priceHistory.length > 100) window.priceHistory.shift();

        Plotly.react('priceChart', [{
          x: window.priceHistory.map(p => p.x),
          y: window.priceHistory.map(p => p.y),
          type: 'scatter',
          mode: 'lines+markers',
          name: '가격',
          line: { color: 'blue' }
        }], {
          title: '실시간 시세',
          xaxis: { title: '시간' },
          yaxis: { title: '가격' }
        });

        // 🏛️ 호가창 시각화 (세로 막대)
        const bids = data.bids?.slice(0, 10).reverse() || [];
        const asks = data.asks?.slice(0, 10) || [];

        Plotly.react('orderbookChart', [
          {
            y: bids.map(b => b[0].toString()),
            x: bids.map(b => b[1]),
            type: 'bar',
            name: '매수',
            orientation: 'h',
            marker: { color: 'green' }
          },
          {
            y: asks.map(a => a[0].toString()),
            x: asks.map(a => a[1]),
            type: 'bar',
            name: '매도',
            orientation: 'h',
            marker: { color: 'red' }
          }
        ], {
          title: '호가창 거래량',
          barmode: 'relative',
          xaxis: { title: '거래량' },
          yaxis: { title: '가격', automargin: true }
        });
    } catch (e) {
        console.error(e);
    }
}
setInterval(refresh, 1000);
refresh();

function toggleTradeLog() {
    const log = document.getElementById('tradeLog');
    log.style.display = (log.style.display === 'none') ? 'block' : 'none';
}

