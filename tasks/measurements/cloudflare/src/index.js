import SpeedTest from '@cloudflare/speedtest';

window.testFinished = false;
window.testInstance = new SpeedTest();
window.testInstance.onFinish = results => {
    window.testResults = results;
    window.testFinished = true;
};
