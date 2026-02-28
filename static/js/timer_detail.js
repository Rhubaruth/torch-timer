// Notifications & Audio
let promise = Notification.requestPermission();

function playSound() {
    let audio = new Audio('/static/sounds/new-notification-09.mp3');
    audio.play();
}

// Update timer locally
var period = 2
const timerBar = document.getElementById('timer-bar');
var seconds_left = JSON.parse(document.getElementById('seconds-left').textContent);
var is_running = JSON.parse(document.getElementById('timer-status').textContent) == "Running";
console.log((seconds_left / 60).toFixed(3));

var real_dur_div = null;

var button_start = null;
var button_pause = null;

function updateRealDuration() {
    if (real_dur_div == null) {
        return null;
    }

    let minutes = Math.floor(seconds_left / 60);
    let seconds = Math.floor(seconds_left % 60);
    real_dur_div.innerText = String(minutes).padStart(2, '0') + ":" + String(seconds).padStart(2, '0');
    return real_dur_div.innerText;
}

real_dur_div = document.getElementById('real-duration');
period = 1
updateRealDuration();

button_start = document.querySelector('#time-start');
button_pause = document.querySelector('#time-pause');

var interval = null;
if (is_running == true) {
    interval = setInterval(updateTime, period * 1000)
}

function updateTimerBar() {
    let timer_value = (seconds_left / 3600) * timerBar.max;
    console.log("Timer Value", timer_value);

    if (timer_value > timerBar.max) {
        timerBar.value = timerBar.max;
    } else if (timer_value <= 0) {
        timerBar.value = 0;
        seconds_left = 0;
    } else {
        timerBar.value = Math.floor(timer_value);
    }
}


function updateTime() {
    seconds_left -= period;
    updateTimerBar();
    updateRealDuration()
    if (seconds_left <= 0 && interval) {
        seconds = 0
        clearInterval(interval);
        playSound();
        alert('Timer ' + timerId + ' timeout!')
        console.log('Timer ' + timerId + ' timeout!')
        return;
    }
}

updateTimerBar();
updateRealDuration();


// WebSocket
const timerId = JSON.parse(document.getElementById('timer-id').textContent);

const chatSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/timer/detail/'
    + timerId
    + '/'
);

function update_state(new_state) {
    if(new_state == "Running") {
        interval = setInterval(updateTime, period * 1000)
        if(button_start) {
        button_start.hidden = true
        button_pause.hidden = false
        }
        return
    }
    if(interval) {
        clearInterval(interval);
    }
    if(button_start) {
        button_start.hidden = false
        button_pause.hidden = true
    }
};

chatSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log(data.type)
    if("time_sync" in data){
        seconds_left = data.time_sync
        updateTimerBar();
        updateRealDuration();
    }

    if(data.type == "update.state") {
        update_state(data.new_state)
    }
};

chatSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

// Add-Remove
document.querySelector('#time-add').onclick = function(e) {
    chatSocket.send(JSON.stringify({
        "time_delta": 60*5.0,
    }));
};
document.querySelector('#time-subtract').onclick = function(e) {
    chatSocket.send(JSON.stringify({
        "time_delta": 60*(-5.0),
    }));
};

// Pause-Play
document.querySelector('#time-pause').onclick = function(e) {
    console.log('Pausing at ' + seconds_left)
    chatSocket.send(JSON.stringify({
        "new_state": "Paused",
    }));
};
document.querySelector('#time-start').onclick = function(e) {
    chatSocket.send(JSON.stringify({
        "new_state": "Running",
    }));
};
