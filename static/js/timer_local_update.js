// Find Elements
const ProgressTimeLeft = document.getElementById('progress-time')
const textState = document.getElementById('text-state')
const textTimeLeft = document.getElementById('text-time')

// Constants
const period = JSON.parse(document.getElementById('var-period').textContent)
const isRunning = JSON.parse(document.getElementById('var-state').textContent) == "Running"

// Variables
var secondsLeft = JSON.parse(document.getElementById('var-seconds').textContent)
var interval = null

if(isRunning) {
    console.log(period)
    interval = setInterval(update, period * 1000, period)
}
update(0)



// Functions
function update(delta) {
    secondsLeft -= delta
    updateTextTimeLeft()
    updateProgressTimeLeft()
    console.log('Left: ' + secondsLeft + '   Delta ' + delta)

    // timeout
    if (secondsLeft <= 0 && interval != null) {
        clearInterval(interval)
        interval = null
        secondsLeft = 0
        updateTextTimeLeft()
        playSound()
        alert('Timer ' + timerId + ' timeout!')
        console.log('Timer ' + timerId + ' timeout!')
        return
    }
}

function updateTextTimeLeft() {
    if (textTimeLeft == null) {
        return false
    }

    let minutes = Math.floor(secondsLeft / 60)
    let seconds = Math.floor(secondsLeft % 60)
    textTimeLeft.innerText = String(minutes).padStart(2, '0') + ":" + String(seconds).padStart(2, '0')
    return true
}

function updateProgressTimeLeft() {
    if (ProgressTimeLeft == null) {
        return false
    }

    let new_value = (secondsLeft / 3600) * ProgressTimeLeft.max

    if (new_value > ProgressTimeLeft.max) {
        ProgressTimeLeft.value = ProgressTimeLeft.max
    } else if (new_value <= 0) {
        ProgressTimeLeft.value = 0
        secondsLeft = 0
    } else {
        ProgressTimeLeft.value = Math.floor(new_value)
    }
    return true
}

