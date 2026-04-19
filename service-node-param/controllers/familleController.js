const Famille = require('../models/Famille');
const Region = require('../models/Region');
const Perimetre = require('../models/Perimetre');

// @desc    Create new famille
// @route   POST /api/familles
// @access  Private (Chef only)
exports.createFamille = async (req, res) => {
    try {
        const { region, perimetre, champs, code_famille, nom_famille, description } = req.body;

        // Check if region exists
        const regionExists = await Region.findOne({ code_region: region });
        if (!regionExists) {
            return res.status(400).json({ message: 'Region does not exist' });
        }

        // Check if perimetre exists in this region
        const perimetreExists = await Perimetre.findOne({ 
            region, 
            code_perimetre: perimetre 
        });
        
        if (!perimetreExists) {
            return res.status(400).json({ 
                message: 'Perimetre does not exist in this region' 
            });
        }

        // Check if famille already exists
        const existingFamille = await Famille.findOne({ 
            region, 
            perimetre, 
            champs, 
            code_famille 
        });
        
        if (existingFamille) {
            return res.status(400).json({ 
                message: 'Famille with these parameters already exists' 
            });
        }

        // Create famille
        const famille = await Famille.create({
            region,
            perimetre,
            champs,
            code_famille,
            nom_famille,
            description,
            created_by: req.user.id || req.user.username
        });

        res.status(201).json({
            success: true,
            data: famille
        });
    } catch (error) {
        console.error('Create famille error:', error);
        res.status(500).json({ 
            message: 'Error creating famille', 
            error: error.message 
        });
    }
};

// @desc    Get all familles
// @route   GET /api/familles
// @access  Private
exports.getAllFamilles = async (req, res) => {
    try {
        const { region, perimetre, champs } = req.query;
        let query = { is_active: true };
        
        if (region) query.region = region;
        if (perimetre) query.perimetre = perimetre;
        if (champs) query.champs = champs;

        const familles = await Famille.find(query)
            .sort({ created_at: -1 });

        res.json({
            success: true,
            count: familles.length,
            data: familles
        });
    } catch (error) {
        console.error('Get familles error:', error);
        res.status(500).json({ 
            message: 'Error fetching familles', 
            error: error.message 
        });
    }
};

// @desc    Get famille by id
// @route   GET /api/familles/:id
// @access  Private
exports.getFamilleById = async (req, res) => {
    try {
        const famille = await Famille.findById(req.params.id);

        if (!famille || !famille.is_active) {
            return res.status(404).json({ message: 'Famille not found' });
        }

        res.json({
            success: true,
            data: famille
        });
    } catch (error) {
        console.error('Get famille error:', error);
        res.status(500).json({ 
            message: 'Error fetching famille', 
            error: error.message 
        });
    }
};

// @desc    Update famille
// @route   PUT /api/familles/:id
// @access  Private (Chef only)
exports.updateFamille = async (req, res) => {
    try {
        const famille = await Famille.findById(req.params.id);

        if (!famille) {
            return res.status(404).json({ message: 'Famille not found' });
        }

        // Update fields
        famille.nom_famille = req.body.nom_famille || famille.nom_famille;
        famille.description = req.body.description || famille.description;
        famille.updated_at = Date.now();

        await famille.save();

        res.json({
            success: true,
            data: famille
        });
    } catch (error) {
        console.error('Update famille error:', error);
        res.status(500).json({ 
            message: 'Error updating famille', 
            error: error.message 
        });
    }
};

// @desc    Delete famille (soft delete)
// @route   DELETE /api/familles/:id
// @access  Private (Chef only)
exports.deleteFamille = async (req, res) => {
    try {
        const famille = await Famille.findById(req.params.id);

        if (!famille) {
            return res.status(404).json({ message: 'Famille not found' });
        }

        famille.is_active = false;
        famille.updated_at = Date.now();
        await famille.save();

        res.json({
            success: true,
            message: 'Famille deleted successfully'
        });
    } catch (error) {
        console.error('Delete famille error:', error);
        res.status(500).json({ 
            message: 'Error deleting famille', 
            error: error.message 
        });
    }
};