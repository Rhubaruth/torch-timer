// Find Elements
const buttonAdd = document.getElementById('button-time-add')
const buttonSubtract = document.getElementById('button-time-subtract')
const buttonStart = document.getElementById('button-time-start')
const buttonPause = document.getElementById('button-time-pause')

const hasOwnerControls = buttonStart && buttonPause

// Constants
const STATE = {
    RUNNING: "Running",
    PAUSED: "Paused",
    FINISHED: "Finished",
}
const timerId = JSON.parse(document.getElementById('var-timerid').textContent)
const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/timer/detail/'
    + timerId
    + '/'
)


// Functions
function update_state(new_state) {
    if(textState != null) {
        textState.innerText = new_state
    }
    if(new_state == STATE.RUNNING) {
        interval = setInterval(update, period * 1000, period)
        if(hasOwnerControls) {
            buttonStart.hidden = true
            buttonPause.hidden = false
        }
    } else if(new_state == STATE.PAUSED) {
        clearInterval(interval)
        interval = null
        if(hasOwnerControls) {
            buttonStart.hidden = false
            buttonPause.hidden = true
        }
    }
}

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data)

    if(data.type == "update.error") {
        console.error('Error' + data.msg)
        return
    } else if(data.type == "update.state") {
        update_state(data.new_state)
    }

    secondsLeft = data.time_sync
    update(0)
}

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly')
    // Reconnect
    setTimeout(chatSocket.connect, 3000)
}

// Add-Remove
if(buttonAdd) {
    buttonAdd.onclick = function(e) {
        chatSocket.send(JSON.stringify({
            "time_delta": 60*5.0,
        }))
    }
}
if(buttonSubtract) {
    buttonSubtract.onclick = function(e) {
        chatSocket.send(JSON.stringify({
            "time_delta": 60*(-5.0),
        }))
    }
}
// Pause-Play
if(buttonStart) {
    buttonStart.onclick = function(e) {
        chatSocket.send(JSON.stringify({
            "new_state": "Running",
        }))
    }
}
if(buttonPause) {
    buttonPause.onclick = function(e) {
        chatSocket.send(JSON.stringify({
            "new_state": "Paused",
        }))
    }
}
