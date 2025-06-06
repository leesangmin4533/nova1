async function refresh() {
    try {
        const res = await fetch('/api/status');
        const data = await res.json();
        document.getElementById('sentiment').innerText = data.sentiment || '-';
        document.getElementById('strategy').innerText = data.strategy || '-';
        document.getElementById('signal').innerText = data.signal || '-';
        document.getElementById('price').innerText = (data.price !== null && data.price !== undefined) ? data.price.toFixed(2) : '-';
        document.getElementById('balance').innerText = (data.balance !== null && data.balance !== undefined) ? data.balance.toFixed(2) : '-';
        if (data.position && data.position.entry_price !== undefined) {
            const rr = (data.position.return_rate * 100).toFixed(2);
            document.getElementById('position').innerText = `${data.position.entry_price} (${rr}%)`;
        } else {
            document.getElementById('position').innerText = '-';
        }
    } catch (e) {
        console.error(e);
    }
}
setInterval(refresh, 1000);
refresh();
