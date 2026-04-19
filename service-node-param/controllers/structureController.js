const Structure = require('../models/Structure');
const Region = require('../models/Region');

// @desc    Create new structure
// @route   POST /api/structures
// @access  Private (Chef/Admin only)
exports.createStructure = async (req, res) => {
    try {
        const { code_structure, type_structure, nom_structure, description, region_id } = req.body;

        // Vérifier que la région existe
        const regionExist = await Region.findById(region_id);
        if (!regionExist || !regionExist.is_active) {
            return res.status(404).json({ message: 'Region not found' });
        }

        // Vérifier unicité type dans cette région
        const existing = await Structure.findOne({
            type_structure: type_structure.toUpperCase(),
            region: region_id
        });
        if (existing) {
            return res.status(400).json({
                message: `Structure '${type_structure}' already exists in this region`
            });
        }

        const structure = await Structure.create({
            code_structure,
            type_structure,
            nom_structure,
            description,
            region: region_id,
            created_by: req.user.id || req.user.username
        });

        res.status(201).json({ success: true, data: structure });

    } catch (error) {
        console.error('Create structure error:', error);
        res.status(500).json({ message: 'Error creating structure', error: error.message });
    }
};

// @desc    Get all structures
// @route   GET /api/structures
// @access  Private
exports.getAllStructures = async (req, res) => {
    try {
        const structures = await Structure.find({ is_active: true })
            .populate('region', 'code_region nom_region')
            .sort({ created_at: -1 });

        res.json({ success: true, count: structures.length, data: structures });

    } catch (error) {
        console.error('Get structures error:', error);
        res.status(500).json({ message: 'Error fetching structures', error: error.message });
    }
};

// @desc    Get all structures by region
// @route   GET /api/structures/region/:id
// @access  Private
exports.getStructuresByRegion = async (req, res) => {
    try {
        const structures = await Structure.find({
            region: req.params.id,
            is_active: true
        })
        .populate('region', 'code_region nom_region')
        .sort({ type_structure: 1 });

        res.json({ success: true, count: structures.length, data: structures });

    } catch (error) {
        console.error('Get structures by region error:', error);
        res.status(500).json({ message: 'Error fetching structures', error: error.message });
    }
};

// @desc    Get structure by ID
// @route   GET /api/structures/:id
// @access  Private
exports.getStructureById = async (req, res) => {
    try {
        const structure = await Structure.findById(req.params.id)
            .populate('region', 'code_region nom_region');

        if (!structure || !structure.is_active) {
            return res.status(404).json({ message: 'Structure not found' });
        }

        res.json({ success: true, data: structure });

    } catch (error) {
        console.error('Get structure error:', error);
        res.status(500).json({ message: 'Error fetching structure', error: error.message });
    }
};

// @desc    Update structure
// @route   PUT /api/structures/:id
// @access  Private (Chef/Admin only)
exports.updateStructure = async (req, res) => {
    try {
        const structure = await Structure.findById(req.params.id);

        if (!structure || !structure.is_active) {
            return res.status(404).json({ message: 'Structure not found' });
        }

        structure.nom_structure  = req.body.nom_structure  || structure.nom_structure;
        structure.description    = req.body.description    || structure.description;
        structure.type_structure = req.body.type_structure || structure.type_structure;

        await structure.save();

        res.json({ success: true, data: structure });

    } catch (error) {
        console.error('Update structure error:', error);
        res.status(500).json({ message: 'Error updating structure', error: error.message });
    }
};

// @desc    Delete structure (soft delete)
// @route   DELETE /api/structures/:id
// @access  Private (Chef/Admin only)
exports.deleteStructure = async (req, res) => {
    try {
        const structure = await Structure.findById(req.params.id);

        if (!structure || !structure.is_active) {
            return res.status(404).json({ message: 'Structure not found' });
        }

        structure.is_active = false;
        await structure.save();

        res.json({ success: true, message: 'Structure deleted successfully' });

    } catch (error) {
        console.error('Delete structure error:', error);
        res.status(500).json({ message: 'Error deleting structure', error: error.message });
    }
};