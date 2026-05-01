// app.js - Configuration de l'application Express
const express = require('express');
const mongoose = require('mongoose');
const dotenv = require('dotenv');
const cors = require('cors');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

// Import routes
const regionRoutes = require('./routes/regionRoutes');
const familleRoutes = require('./routes/familleRoutes');
const perimetreRoutes = require('./routes/perimetreRoutes');
const structureRoutes = require('./routes/structureRoutes');
const directionRoutes = require('./routes/directionRoutes');
const departementRoutes = require('./routes/departementRoutes');
const  familleDirectionRoutes = require('./routes/familleDirectionRoutes');



dotenv.config({ path: './config.env' });

const app = express();

// Security middleware
app.use(helmet());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.set('trust proxy', 1);
// Rate limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // limit each IP to 100 requests per windowMs
});
app.use('/api', limiter);

// Routes
app.use('/api/regions', regionRoutes);
app.use('/api/familles', familleRoutes);
app.use('/api/perimetres', perimetreRoutes);
app.use('/api/structures', structureRoutes);
app.use('/api/directions', directionRoutes);
app.use('/api/departements', departementRoutes);
app.use('/api//direction/', familleDirectionRoutes);

// Health check endpoint
app.get('/health', (req, res) => {
    res.status(200).json({ status: 'UP' });
});

// Info endpoint
app.get('/info', (req, res) => {
    res.json({
        service: 'service-node-param',
        version: '1.0.0',
        status: 'running'
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(err.status || 500).json({
        message: err.message || 'Internal server error',
        error: process.env.NODE_ENV === 'development' ? err : {}
    });
});

module.exports = app;