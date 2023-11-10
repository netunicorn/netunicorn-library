import SpeedTest from '@cloudflare/speedtest';

window.testFinished = false;
const test = new SpeedTest();
test.onFinish = results => {
    window.testResults = results;
    window.testFinished = true;
};
