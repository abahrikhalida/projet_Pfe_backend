// server.js
const dotenv = require('dotenv');
dotenv.config({ path: './config.env' }); // ← DOIT ÊTRE EN PREMIER

const mongoose = require('mongoose');
const app = require('./app');
const eurekaService = require('./services/eurekaService');

const PORT = process.env.PORT || 3002;

mongoose.connect(process.env.MONGODB_URI)
    .then(() => {
        console.log('✅ MongoDB connected successfully');

        const server = app.listen(PORT, () => {
            console.log(`🚀 Server running on port ${PORT}`);
            eurekaService.registerWithEureka(server);
        });

        process.on('SIGINT', () => {
            console.log('\n🛑 Shutting down gracefully...');
            server.close(() => {
                console.log('👋 Server closed');
                mongoose.connection.close(false, () => {
                    console.log('🔌 MongoDB connection closed');
                    process.exit(0);
                });
            });
        });
    })
    .catch(err => {
        console.error('❌ MongoDB connection error:', err);
        process.exit(1);
    });