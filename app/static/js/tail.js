var ws
function initiate_pull(uri){
    ws = new WebSocket(uri)
    ws.onmessage = function(event) {
        document.getElementById('logspace').innerHTML += event.data
    }
    ws.onopen = function(event) {
        ws.send('start_sending')
    }
    ws.onclose = function(event) {
        window.alert(event.reason)
        console.log(event)
    }
};

