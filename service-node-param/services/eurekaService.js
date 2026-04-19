const eurekaClient = require('../config/eureka');

class EurekaService {
    registerWithEureka(app) {
        try {
            eurekaClient.start(error => {
                if (error) {
                    console.log('Failed to register with Eureka:', error);
                } else {
                    console.log('Registered with Eureka successfully');
                    
                    // Handle graceful shutdown
                    this.setupGracefulShutdown();
                }
            });

            // Add Eureka event listeners
            eurekaClient.on('started', () => {
                console.log('Eureka client started');
            });

            eurekaClient.on('registered', () => {
                console.log('Eureka client registered');
            });

            eurekaClient.on('deregistered', () => {
                console.log('Eureka client deregistered');
            });

            eurekaClient.on('heartbeat', () => {
                console.log('Eureka heartbeat sent');
            });

        } catch (error) {
            console.error('Error registering with Eureka:', error);
        }
    }

    setupGracefulShutdown() {
        process.on('SIGINT', () => {
            console.log('Shutting down gracefully...');
            eurekaClient.stop(() => {
                console.log('Deregistered from Eureka');
                process.exit();
            });
        });

        process.on('SIGTERM', () => {
            console.log('Received SIGTERM, shutting down...');
            eurekaClient.stop(() => {
                console.log('Deregistered from Eureka');
                process.exit();
            });
        });
    }

    getServiceUrl(serviceName) {
        return new Promise((resolve, reject) => {
            try {
                const instances = eurekaClient.getInstancesByAppId(serviceName);
                
                if (instances && instances.length > 0) {
                    const instance = instances[0];
                    const url = `http://${instance.hostName}:${instance.port.$}`;
                    resolve(url);
                } else {
                    reject(new Error(`No instances found for service: ${serviceName}`));
                }
            } catch (error) {
                reject(error);
            }
        });
    }
}

module.exports = new EurekaService();