const FamilleDirection = require('../models/FamilleDirection');
const Direction = require('../models/Direction');

// Create famille direction
exports.createFamilleDirection = async (req, res) => {
    try {
        const direction = await Direction.findById(req.body.direction);
        if (!direction) {
            return res.status(404).json({
                success: false,
                message: 'Direction not found'
            });
        }
        
        const familleDirection = new FamilleDirection(req.body);
        await familleDirection.save();
        await familleDirection.populate('direction', 'code_direction nom_direction');
        
        res.status(201).json({
            success: true,
            data: familleDirection
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};

// Get all familles direction
exports.getAllFamillesDirection = async (req, res) => {
    try {
        const familles = await FamilleDirection.find({ is_active: true })
            .populate('direction', 'code_direction nom_direction')
            .sort({ code_famille: 1 });
        res.status(200).json({
            success: true,
            count: familles.length,
            data: familles
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};

// Get familles by direction
exports.getFamillesByDirection = async (req, res) => {
    try {
        const familles = await FamilleDirection.find({ 
            direction: req.params.directionId,
            is_active: true 
        }).populate('direction', 'code_direction nom_direction');
        
        res.status(200).json({
            success: true,
            count: familles.length,
            data: familles
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};

// Get famille by ID
exports.getFamilleDirectionById = async (req, res) => {
    try {
        const famille = await FamilleDirection.findById(req.params.id)
            .populate('direction', 'code_direction nom_direction');
        if (!famille) {
            return res.status(404).json({
                success: false,
                message: 'Famille not found'
            });
        }
        res.status(200).json({
            success: true,
            data: famille
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};

// Get famille by code
exports.getFamilleDirectionByCode = async (req, res) => {
    try {
        const famille = await FamilleDirection.findOne({ code_famille: req.params.code, is_active: true })
            .populate('direction', 'code_direction nom_direction');
        if (!famille) {
            return res.status(404).json({
                success: false,
                message: 'Famille not found'
            });
        }
        res.status(200).json({
            success: true,
            data: famille
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};

// Update famille
exports.updateFamilleDirection = async (req, res) => {
    try {
        const famille = await FamilleDirection.findByIdAndUpdate(
            req.params.id,
            { ...req.body, updated_at: Date.now() },
            { new: true, runValidators: true }
        ).populate('direction', 'code_direction nom_direction');
        
        if (!famille) {
            return res.status(404).json({
                success: false,
                message: 'Famille not found'
            });
        }
        res.status(200).json({
            success: true,
            data: famille
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};

// Delete famille (soft delete)
exports.deleteFamilleDirection = async (req, res) => {
    try {
        const famille = await FamilleDirection.findByIdAndUpdate(
            req.params.id,
            { is_active: false, updated_at: Date.now() },
            { new: true }
        );
        if (!famille) {
            return res.status(404).json({
                success: false,
                message: 'Famille not found'
            });
        }
        res.status(200).json({
            success: true,
            message: 'Famille deleted successfully'
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};

// Hard delete famille
exports.hardDeleteFamilleDirection = async (req, res) => {
    try {
        const famille = await FamilleDirection.findByIdAndDelete(req.params.id);
        if (!famille) {
            return res.status(404).json({
                success: false,
                message: 'Famille not found'
            });
        }
        res.status(200).json({
            success: true,
            message: 'Famille permanently deleted'
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};