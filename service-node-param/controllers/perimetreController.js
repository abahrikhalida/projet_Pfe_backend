const Perimetre = require('../models/Perimetre');
const Region = require('../models/Region');
const mongoose = require('mongoose');  

// @desc    Create new perimetre
// @route   POST /api/perimetres
// @access  Private (Chef only)
exports.createPerimetre = async (req, res) => {
    try {
        const { region, code_perimetre, nom_perimetre, description } = req.body;

        // Check if region exists
        const regionExists = await Region.findOne({ code_region: region });
        if (!regionExists) {
            return res.status(400).json({ message: 'Region does not exist' });
        }

        // Check if perimetre already exists in this region
        const existingPerimetre = await Perimetre.findOne({ 
            region, 
            code_perimetre 
        });
        
        if (existingPerimetre) {
            return res.status(400).json({ 
                message: 'Perimetre with this code already exists in this region' 
            });
        }

        // Create perimetre
        const perimetre = await Perimetre.create({
            region,
            code_perimetre,
            nom_perimetre,
            description,
            created_by: req.user.id || req.user.username
        });

        res.status(201).json({
            success: true,
            data: perimetre
        });
    } catch (error) {
        console.error('Create perimetre error:', error);
        res.status(500).json({ 
            message: 'Error creating perimetre', 
            error: error.message 
        });
    }
};

// @desc    Get all perimetres
// @route   GET /api/perimetres
// @access  Private
exports.getAllPerimetres = async (req, res) => {
    try {
        const { region } = req.query;
        let query = { is_active: true };
        
        if (region) {
            query.region = region;
        }

        const perimetres = await Perimetre.find(query)
            .sort({ created_at: -1 });

        res.json({
            success: true,
            count: perimetres.length,
            data: perimetres
        });
    } catch (error) {
        console.error('Get perimetres error:', error);
        res.status(500).json({ 
            message: 'Error fetching perimetres', 
            error: error.message 
        });
    }
};

// @desc    Get perimetre by code
// @route   GET /api/perimetres/:code
// @access  Private
exports.getPerimetreByCode = async (req, res) => {
    try {
        const perimetre = await Perimetre.findOne({ 
            code_perimetre: req.params.code,
            is_active: true 
        });

        if (!perimetre) {
            return res.status(404).json({ message: 'Perimetre not found' });
        }

        res.json({
            success: true,
            data: perimetre
        });
    } catch (error) {
        console.error('Get perimetre error:', error);
        res.status(500).json({ 
            message: 'Error fetching perimetre', 
            error: error.message 
        });
    }
};

// @desc    Update perimetre
// @route   PUT /api/perimetres/:code
// @access  Private (Chef only)
exports.updatePerimetre = async (req, res) => {
    try {
        const perimetre = await Perimetre.findOne({ 
            code_perimetre: req.params.code 
        });

        if (!perimetre) {
            return res.status(404).json({ message: 'Perimetre not found' });
        }

        // Update fields
        perimetre.nom_perimetre = req.body.nom_perimetre || perimetre.nom_perimetre;
        perimetre.description = req.body.description || perimetre.description;
        perimetre.updated_at = Date.now();

        await perimetre.save();

        res.json({
            success: true,
            data: perimetre
        });
    } catch (error) {
        console.error('Update perimetre error:', error);
        res.status(500).json({ 
            message: 'Error updating perimetre', 
            error: error.message 
        });
    }
};

// @desc    Delete perimetre (soft delete)
// @route   DELETE /api/perimetres/:code
// @access  Private (Chef only)
exports.deletePerimetre = async (req, res) => {
    try {
        const perimetre = await Perimetre.findOne({ 
            code_perimetre: req.params.code 
        });

        if (!perimetre) {
            return res.status(404).json({ message: 'Perimetre not found' });
        }

        perimetre.is_active = false;
        perimetre.updated_at = Date.now();
        await perimetre.save();

        res.json({
            success: true,
            message: 'Perimetre deleted successfully'
        });
    } catch (error) {
        console.error('Delete perimetre error:', error);
        res.status(500).json({ 
            message: 'Error deleting perimetre', 
            error: error.message 
        });
    }
};
// @desc    Get perimetre by ID
// @route   GET /api/perimetres/id/:id
// @access  Private
exports.getPerimetreById = async (req, res) => {
    try {
        const { id } = req.params;

        const perimetre = await Perimetre.findOne({
            _id: id,
            is_active: true
        });

        if (!perimetre) {
            return res.status(404).json({
                success: false,
                message: 'Perimetre not found'
            });
        }

        res.status(200).json({
            success: true,
            data: perimetre
        });

    } catch (error) {
        console.error('Get perimetre by ID error:', error);

        // 🔥 Gestion erreur ObjectId invalide
        if (error.name === 'CastError') {
            return res.status(400).json({
                success: false,
                message: 'Invalid perimetre ID'
            });
        }

        res.status(500).json({
            success: false,
            message: 'Error fetching perimetre',
            error: error.message
        });
    }
};

// @desc    Get perimetres by region ObjectId
// @route   GET /api/perimetres/region/:regionId
// @access  Private
exports.getPerimetresByRegionId = async (req, res) => {
    try {
        const { regionId } = req.params;
        
        // Vérifier si l'ID est valide
        const isValidObjectId = mongoose.Types.ObjectId.isValid(regionId);
        if (!isValidObjectId) {
            return res.status(400).json({
                success: false,
                message: 'ID de région invalide'
            });
        }
        
        // 1. Trouver la région par son ObjectId
        const region = await Region.findById(regionId);
        if (!region) {
            return res.status(404).json({
                success: false,
                message: 'Région non trouvée'
            });
        }
        
        // 2. Récupérer les périmètres avec le code_region de cette région
        const perimetres = await Perimetre.find({ 
            region: region.code_region,
            is_active: true 
        }).sort({ created_at: -1 });
        
        res.json({
            success: true,
            count: perimetres.length,
            data: perimetres
        });
    } catch (error) {
        console.error('Get perimetres by region ID error:', error);
        res.status(500).json({ 
            success: false,
            message: 'Error fetching perimetres', 
            error: error.message 
        });
    }
};
exports.getPerimetresByCodeRegion = async (req, res) => {
    try {
        const { codeRegion } = req.params;

        const perimetres = await Perimetre.find({
            region: codeRegion,
            is_active: true
        }).sort({ created_at: -1 });

        res.json({
            success: true,
            count: perimetres.length,
            data: perimetres
        });

    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({
            success: false,
            message: 'Error fetching perimetres',
            error: error.message
        });
    }
};
