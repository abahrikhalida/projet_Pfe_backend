// test-create.js
const express = require('express');
const mongoose = require('mongoose');

// ==================== MODÈLES ====================
// Modèle Region simplifié
const regionSchema = new mongoose.Schema({
    code_region: { type: String, required: true, unique: true },
    nom_region: { type: String, required: true },
    description: String,
    created_by: { type: String, default: 'test-user' },
    created_at: { type: Date, default: Date.now },
    is_active: { type: Boolean, default: true }
});

// Modèle Perimetre simplifié
const perimetreSchema = new mongoose.Schema({
    region: { type: String, required: true },
    code_perimetre: { type: String, required: true },
    nom_perimetre: { type: String, required: true },
    description: String,
    created_by: { type: String, default: 'test-user' },
    created_at: { type: Date, default: Date.now },
    is_active: { type: Boolean, default: true }
});

// Modèle Famille simplifié
const familleSchema = new mongoose.Schema({
    region: { type: String, required: true },
    perimetre: { type: String, required: true },
    champs: { type: String, required: true },
    code_famille: { type: String, required: true },
    nom_famille: { type: String, required: true },
    description: String,
    created_by: { type: String, default: 'test-user' },
    created_at: { type: Date, default: Date.now },
    is_active: { type: Boolean, default: true }
});

// Création des modèles
const Region = mongoose.model('Region', regionSchema);
const Perimetre = mongoose.model('Perimetre', perimetreSchema);
const Famille = mongoose.model('Famille', familleSchema);

// ==================== SERVEUR EXPRESS ====================
const app = express();
app.use(express.json());

// ==================== ROUTES SANS AUTH ====================

// Route pour créer une région
app.post('/api/test/regions', async (req, res) => {
    try {
        const { code_region, nom_region, description } = req.body;
        
        const region = await Region.create({
            code_region,
            nom_region,
            description: description || `Description de ${nom_region}`,
            created_by: 'test-user'
        });
        
        res.status(201).json({
            success: true,
            message: 'Région créée avec succès',
            data: region
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
});

// Route pour créer un périmètre
app.post('/api/test/perimetres', async (req, res) => {
    try {
        const { region, code_perimetre, nom_perimetre, description } = req.body;
        
        // Vérifier si la région existe
        const regionExists = await Region.findOne({ code_region: region });
        if (!regionExists) {
            return res.status(404).json({
                success: false,
                message: `Région ${region} n'existe pas`
            });
        }
        
        const perimetre = await Perimetre.create({
            region,
            code_perimetre,
            nom_perimetre,
            description: description || `Description de ${nom_perimetre}`,
            created_by: 'test-user'
        });
        
        res.status(201).json({
            success: true,
            message: 'Périmètre créé avec succès',
            data: perimetre
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
});

// Route pour créer une famille
app.post('/api/test/familles', async (req, res) => {
    try {
        const { region, perimetre, champs, code_famille, nom_famille, description } = req.body;
        
        // Vérifier si la région existe
        const regionExists = await Region.findOne({ code_region: region });
        if (!regionExists) {
            return res.status(404).json({
                success: false,
                message: `Région ${region} n'existe pas`
            });
        }
        
        // Vérifier si le périmètre existe
        const perimetreExists = await Perimetre.findOne({ 
            region, 
            code_perimetre: perimetre 
        });
        if (!perimetreExists) {
            return res.status(404).json({
                success: false,
                message: `Périmètre ${perimetre} n'existe pas dans la région ${region}`
            });
        }
        
        const famille = await Famille.create({
            region,
            perimetre,
            champs,
            code_famille,
            nom_famille,
            description: description || `Description de ${nom_famille}`,
            created_by: 'test-user'
        });
        
        res.status(201).json({
            success: true,
            message: 'Famille créée avec succès',
            data: famille
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
});

// Route pour lister toutes les données
app.get('/api/test/all', async (req, res) => {
    try {
        const regions = await Region.find();
        const perimetres = await Perimetre.find();
        const familles = await Famille.find();
        
        res.json({
            success: true,
            counts: {
                regions: regions.length,
                perimetres: perimetres.length,
                familles: familles.length
            },
            data: {
                regions,
                perimetres,
                familles
            }
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
});

// Route pour nettoyer les données de test
app.delete('/api/test/clean', async (req, res) => {
    try {
        await Region.deleteMany({ created_by: 'test-user' });
        await Perimetre.deleteMany({ created_by: 'test-user' });
        await Famille.deleteMany({ created_by: 'test-user' });
        
        res.json({
            success: true,
            message: 'Toutes les données de test ont été supprimées'
        });
    } catch (error) {
        res.status(500).json({
            success: false,
            message: error.message
        });
    }
});

// ==================== FONCTION DE TEST ====================
async function runTests() {
    console.log('🚀 Démarrage des tests de création...\n');
    
    try {
        // 1. Créer une région
        console.log('1️⃣ Création d\'une région...');
        const regionRes = await fetch('http://localhost:3000/api/test/regions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                code_region: 'REG001',
                nom_region: 'Région Centre'
            })
        });
        const regionData = await regionRes.json();
        console.log('   ✅ Région créée:', regionData.data.code_region, '-', regionData.data.nom_region);
        
        // 2. Créer un périmètre
        console.log('\n2️⃣ Création d\'un périmètre...');
        const perimetreRes = await fetch('http://localhost:3000/api/test/perimetres', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                region: 'REG001',
                code_perimetre: 'PER001',
                nom_perimetre: 'Périmètre Nord'
            })
        });
        const perimetreData = await perimetreRes.json();
        console.log('   ✅ Périmètre créé:', perimetreData.data.code_perimetre, '-', perimetreData.data.nom_perimetre);
        
        // 3. Créer une famille
        console.log('\n3️⃣ Création d\'une famille...');
        const familleRes = await fetch('http://localhost:3000/api/test/familles', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                region: 'REG001',
                perimetre: 'PER001',
                champs: 'Champs A',
                code_famille: 'FAM001',
                nom_famille: 'Famille Test'
            })
        });
        const familleData = await familleRes.json();
        console.log('   ✅ Famille créée:', familleData.data.code_famille, '-', familleData.data.nom_famille);
        
        // 4. Vérifier toutes les données
        console.log('\n4️⃣ Vérification des données...');
        const allRes = await fetch('http://localhost:3000/api/test/all');
        const allData = await allRes.json();
        console.log('   📊 Statistiques:');
        console.log(`      - Régions: ${allData.counts.regions}`);
        console.log(`      - Périmètres: ${allData.counts.perimetres}`);
        console.log(`      - Familles: ${allData.counts.familles}`);
        
        console.log('\n✅ Tous les tests sont réussis !\n');
        
    } catch (error) {
        console.error('❌ Erreur pendant les tests:', error.message);
    }
}

// ==================== DÉMARRAGE DU SERVEUR ====================
const PORT = 3000;
const MONGODB_URI = 'mongodb://root:root@localhost:27017/parametre_db?authSource=admin';

mongoose.connect(MONGODB_URI)
    .then(() => {
        console.log('✅ Connecté à MongoDB\n');
        
        app.listen(PORT, () => {
            console.log(`🚀 Serveur de test démarré sur http://localhost:${PORT}`);
            console.log('\n📝 Routes disponibles:');
            console.log('   POST   /api/test/regions    - Créer une région');
            console.log('   POST   /api/test/perimetres - Créer un périmètre');
            console.log('   POST   /api/test/familles   - Créer une famille');
            console.log('   GET    /api/test/all        - Voir toutes les données');
            console.log('   DELETE /api/test/clean      - Nettoyer les données de test\n');
            
            // Lancer les tests automatiquement après 2 secondes
            setTimeout(() => {
                runTests();
            }, 2000);
        });
    })
    .catch(err => {
        console.error('❌ Erreur de connexion MongoDB:', err.message);
        process.exit(1);
    });