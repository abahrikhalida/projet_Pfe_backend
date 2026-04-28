const Direction = require('../models/Direction');
const Departement = require('../models/Departement');
const FamilleDirection = require('../models/FamilleDirection');

// Create direction
exports.createDirection = async (req, res) => {
    try {
        const direction = new Direction(req.body);
        await direction.save();
        res.status(201).json({
            success: true,
            data: direction
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};

// Get all directions
exports.getAllDirections = async (req, res) => {
    try {
        const directions = await Direction.find({ is_active: true }).sort({ code_direction: 1 });
        res.status(200).json({
            success: true,
            count: directions.length,
            data: directions
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};

// Get direction by ID
exports.getDirectionById = async (req, res) => {
    try {
        const direction = await Direction.findById(req.params.id);
        if (!direction) {
            return res.status(404).json({
                success: false,
                message: 'Direction not found'
            });
        }
        res.status(200).json({
            success: true,
            data: direction
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};

// Get direction by code
exports.getDirectionByCode = async (req, res) => {
    try {
        const direction = await Direction.findOne({ code_direction: req.params.code, is_active: true });
        if (!direction) {
            return res.status(404).json({
                success: false,
                message: 'Direction not found'
            });
        }
        res.status(200).json({
            success: true,
            data: direction
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};

// Update direction
exports.updateDirection = async (req, res) => {
    try {
        const direction = await Direction.findByIdAndUpdate(
            req.params.id,
            { ...req.body, updated_at: Date.now() },
            { new: true, runValidators: true }
        );
        if (!direction) {
            return res.status(404).json({
                success: false,
                message: 'Direction not found'
            });
        }
        res.status(200).json({
            success: true,
            data: direction
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};

// Delete direction (soft delete)
exports.deleteDirection = async (req, res) => {
    try {
        const direction = await Direction.findByIdAndUpdate(
            req.params.id,
            { is_active: false, updated_at: Date.now() },
            { new: true }
        );
        if (!direction) {
            return res.status(404).json({
                success: false,
                message: 'Direction not found'
            });
        }
        res.status(200).json({
            success: true,
            message: 'Direction deleted successfully'
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};

// Hard delete direction (permanent)
exports.hardDeleteDirection = async (req, res) => {
    try {
        // Also delete all related departements and familles
        await Departement.deleteMany({ direction: req.params.id });
        await FamilleDirection.deleteMany({ direction: req.params.id });
        
        const direction = await Direction.findByIdAndDelete(req.params.id);
        if (!direction) {
            return res.status(404).json({
                success: false,
                message: 'Direction not found'
            });
        }
        res.status(200).json({
            success: true,
            message: 'Direction and all related data permanently deleted'
        });
    } catch (error) {
        res.status(400).json({
            success: false,
            message: error.message
        });
    }
};