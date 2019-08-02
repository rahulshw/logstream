var ws
function initiate_pull(uri){
    ws = new WebSocket(uri)
    ws.onmessage = function(event) {
        document.getElementById('logspace').innerHTML += event.data
        // if the page was scrolled to bottom, scroll to bottom
        if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight)
            window.scrollTo(0,document.body.scrollHeight)
    }
    ws.onopen = function(event) {
        ws.send('start_sending')
    }
    ws.onclose = function(event) {
        window.alert(event.reason)
        console.log(event)
    }
};