const mqtt = require('mqtt');

const { MQTT_BROKER_URL } = process.env;

// const QOS_LEVEL1 = 1; // 不能用 process.env;讀取
const QOS_LEVEL = parseInt(process.env.QOS_LEVEL, 10); // env讀到的是字串

// 初始化 MQTT 客戶端
const mqttClient = mqtt.connect(MQTT_BROKER_URL);

mqttClient.on('connect', () => {
  console.log('MQTT connected');
});

// 封裝發送消息的函數
function publishMessage(topic, message) {
  mqttClient.publish(topic, message, { qos: QOS_LEVEL }, (err) => {
    if (err) {
      console.error(`Publish error on topic ${topic}:`, err);
    } else {
      // console.log(`Message sent to topic '${topic}':`, message);
    }
  });
}

module.exports = {
  mqttClient,
  publishMessage,
};
