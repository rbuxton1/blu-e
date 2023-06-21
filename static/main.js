const scale = (input, inputRange, outputRange) => {
    let [inMin, inMax] = inputRange;
    let [outMin, outMax] = outputRange;
    let s = (input - inMin) / (inMax - inMin);
    return s * (outMax - outMin) + outMin;
}

const socket = io();
socket.on('connect', () => {
    console.log('Connected!');
})

let left = new JoyStick('leftStick', {},  (data) => {
    let motionSpeed = document.getElementById('moveSpeed').value;
    let turnSpeed = document.getElementById('turnSpeed').value;
    let motion = scale(data.y, [-100, 100], [-motionSpeed, motionSpeed]);
    let turn = scale(data.x, [-100, 100], [-turnSpeed, turnSpeed]);
    console.log('motion', motion, 'turn', turn)

    socket.emit('command', { cmd: 'move', step: motion, direction: 'x' });
    socket.emit('command', { cmd: 'turn', step: -turn });
});

let right = new JoyStick('rightStick', {}, (data) => {
    let pitch = scale(data.y, [-100, 100], [-10, 10]);
    let yaw = scale(data.x, [-100, 100], [-12, 12]);

    socket.emit('command', { cmd: 'attitude', direction: 'p', step: pitch });
    socket.emit('command', { cmd: 'attitude', direction: 'y', step: -yaw });
});

const baseSlider = document.getElementById('armBase');
const jointSlider = document.getElementById('armJoint');
const clawSlider = document.getElementById('claw');
baseSlider.addEventListener('input', (data) => {
    console.log('data', data);
    socket.emit('command', { cmd: 'motor', id: 53, step: data.target.value});
});
jointSlider.addEventListener('input', (data) => {
    socket.emit('command', { cmd: 'motor', id: 52, step: data.target.value});
});
clawSlider.addEventListener('input', (data) => {
    socket.emit('command', { cmd: 'motor', id: 51, step: data.target.value});
});

const transXSlider = document.getElementById('transX');
const transYSlider = document.getElementById('transY');
const transZSlider = document.getElementById('transZ');
transXSlider.addEventListener('input', (data) => {
    socket.emit('command', { cmd: 'translate', direction: 'x', step: data.target.value});
});
transYSlider.addEventListener('input', (data) => {
    socket.emit('command', { cmd: 'translate', direction: 'y', step: data.target.value});
});
transZSlider.addEventListener('input', (data) => {
    socket.emit('command', { cmd: 'translate', direction: 'z', step: data.target.value});
});

const imuCheck = document.getElementById('imuCheck')
imuCheck.addEventListener('change', (data) => {
    socket.emit('command', { cmd: 'imu', mode: data.target.checked ? 1 : 0})
});

const gaitSelect = document.getElementById('gaitSelect');
gaitSelect.addEventListener('change', (data) => {
    socket.emit('command', { cmd: 'gait', mode: data.target.value });
});

const paceSelect = document.getElementById('paceSelect');
paceSelect.addEventListener('change', (data) => {
    socket.emit('command', { cmd: 'pace', mode: data.target.value });
});

socket.on('status', (payload) => {
    const statusString = document.getElementById('statusString');
    statusString.innerHTML = `Batt ${payload.battery}%`
})