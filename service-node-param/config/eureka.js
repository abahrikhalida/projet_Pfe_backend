// config/eureka.js
const Eureka = require('eureka-js-client').Eureka;
const dotenv = require('dotenv');
const os = require('os');

dotenv.config({ path: './config.env' });

// Récupérer l'adresse IP locale pour que Eureka puisse la résoudre
const getLocalIp = () => {
    const interfaces = os.networkInterfaces();
    for (const name of Object.keys(interfaces)) {
        for (const iface of interfaces[name]) {
            if (iface.family === 'IPv4' && !iface.internal) {
                return iface.address;
            }
        }
    }
    return '127.0.0.1';
};

const eurekaHost = process.env.EUREKA_HOST || 'localhost';
const eurekaPort = process.env.EUREKA_PORT || 8761;
const hostName = process.env.EUREKA_INSTANCE_HOST || getLocalIp();
const servicePort = process.env.PORT || 3002;
const serviceName = process.env.EUREKA_SERVICE_NAME || 'SERVICE-NODE-PARAM';

console.log('🔧 Configuration Eureka:');
console.log(`   Service: ${serviceName}`);
console.log(`   Host: ${hostName}`);
console.log(`   Port: ${servicePort}`);
console.log(`   Eureka Server: ${eurekaHost}:${eurekaPort}`);
console.log(`   IP Address: ${getLocalIp()}`);

const eurekaClient = new Eureka({
    instance: {
        app: serviceName,
        instanceId: `${serviceName}:${hostName}:${servicePort}`,
        hostName: hostName,
        ipAddr: getLocalIp(),
        port: {
            '$': parseInt(servicePort),
            '@enabled': 'true',
        },
        vipAddress: serviceName,
        dataCenterInfo: {
            '@class': 'com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo',
            name: 'MyOwn',
        },
        statusPageUrl: `http://${hostName}:${servicePort}/info`,
        healthCheckUrl: `http://${hostName}:${servicePort}/health`,
        homePageUrl: `http://${hostName}:${servicePort}`,
        metadata: {
            'nodejs': 'true',
            'version': '1.0.0',
            'environment': process.env.NODE_ENV || 'development',
            'port': servicePort.toString(),
            'docker': 'false'
        }
    },
    eureka: {
        host: eurekaHost,
        port: parseInt(eurekaPort),
        servicePath: '/eureka/apps/',
        maxRetries: 10,
        requestRetryDelay: 2000,
        preferSameZone: true,
        registerWithEureka: true,
        fetchRegistry: true
    }
});

module.exports = eurekaClient;