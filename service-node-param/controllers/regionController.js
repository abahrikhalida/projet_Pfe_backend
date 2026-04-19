const Region = require('../models/Region');

// @desc    Create new region
// @route   POST /api/regions
// @access  Private (Chef only)
exports.createRegion = async (req, res) => {
    try {
        const { code_region, nom_region, description } = req.body;

        // Check if region already exists
        const existingRegion = await Region.findOne({ code_region });
        if (existingRegion) {
            return res.status(400).json({ 
                message: 'Region with this code already exists' 
            });
        }

        // Create region
        const region = await Region.create({
            code_region,
            nom_region,
            description,
            created_by: req.user.id || req.user.username
        });

        res.status(201).json({
            success: true,
            data: region
        });
    } catch (error) {
        console.error('Create region error:', error);
        res.status(500).json({ 
            message: 'Error creating region', 
            error: error.message 
        });
    }
};

// @desc    Get all regions
// @route   GET /api/regions
// @access  Private
exports.getAllRegions = async (req, res) => {
    try {
        const regions = await Region.find({ is_active: true })
            .sort({ created_at: -1 });

        res.json({
            success: true,
            count: regions.length,
            data: regions
        });
    } catch (error) {
        console.error('Get regions error:', error);
        res.status(500).json({ 
            message: 'Error fetching regions', 
            error: error.message 
        });
    }
};

// @desc    Get region by code
// @route   GET /api/regions/:code
// @access  Private
exports.getRegionByCode = async (req, res) => {
    try {
        const region = await Region.findOne({ 
            code_region: req.params.code,
            is_active: true 
        });

        if (!region) {
            return res.status(404).json({ message: 'Region not found' });
        }

        res.json({
            success: true,
            data: region
        });
    } catch (error) {
        console.error('Get region error:', error);
        res.status(500).json({ 
            message: 'Error fetching region', 
            error: error.message 
        });
    }
};

// @desc    Update region
// @route   PUT /api/regions/:code
// @access  Private (Chef only)
exports.updateRegion = async (req, res) => {
    try {
        const region = await Region.findOne({ 
            code_region: req.params.code 
        });

        if (!region) {
            return res.status(404).json({ message: 'Region not found' });
        }

        // Update fields
        region.nom_region = req.body.nom_region || region.nom_region;
        region.description = req.body.description || region.description;
        region.updated_at = Date.now();

        await region.save();

        res.json({
            success: true,
            data: region
        });
    } catch (error) {
        console.error('Update region error:', error);
        res.status(500).json({ 
            message: 'Error updating region', 
            error: error.message 
        });
    }
};

// @desc    Delete region (soft delete)
// @route   DELETE /api/regions/:code
// @access  Private (Chef only)
exports.deleteRegion = async (req, res) => {
    try {
        const region = await Region.findOne({ 
            code_region: req.params.code 
        });

        if (!region) {
            return res.status(404).json({ message: 'Region not found' });
        }

        region.is_active = false;
        region.updated_at = Date.now();
        await region.save();

        res.json({
            success: true,
            message: 'Region deleted successfully'
        });
    } catch (error) {
        console.error('Delete region error:', error);
        res.status(500).json({ 
            message: 'Error deleting region', 
            error: error.message 
        });
    }
};
// @desc    Get region by ID
// @route   GET /api/regions/id/:id
// @access  Private
// exports.getRegionById = async (req, res) => {
//     try {
//         const { id } = req.params;

//         const region = await Region.findOne({
//             _id: id,
//             is_active: true
//         });

//         if (!region) {
//             return res.status(404).json({
//                 success: false,
//                 message: 'Region not found'
//             });
//         }

//         res.status(200).json({
//             success: true,
//             data: region
//         });

//     } catch (error) {
//         console.error('Get region by ID error:', error);

//         // Handle invalid ObjectId (very important)
//         if (error.name === 'CastError') {
//             return res.status(400).json({
//                 success: false,
//                 message: 'Invalid region ID'
//             });
//         }

//         res.status(500).json({
//             success: false,
//             message: 'Error fetching region',
//             error: error.message
//         });
//     }
// };
exports.getRegionById = async (req, res) => {
    try {
        const { id } = req.params;

        const region = await Region.findOne({
            _id: id,
            is_active: true
        });

        if (!region) {
            return res.status(404).json({
                success: false,
                message: 'Region not found'
            });
        }

        res.status(200).json({
            success: true,
            data: region
        });

    } catch (error) {
        console.error('Get region by ID error:', error);

        // Handle invalid ObjectId (very important)
        if (error.name === 'CastError') {
            return res.status(400).json({
                success: false,
                message: 'Invalid region ID'
            });
        }

        res.status(500).json({
            success: false,
            message: 'Error fetching region',
            error: error.message
        });
    }
};
