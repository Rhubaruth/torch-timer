// Notifications & Audio
let promise = Notification.requestPermission();

function playSound() {
    let audio = new Audio('/static/sounds/new-notification-09.mp3');
    audio.play();
}
