// controllers/departementController.js
const Departement = require('../models/Departement');
const Direction = require('../models/Direction');

// Create departement
exports.createDepartement = async (req, res) => {
    try {
        const { direction, code_departement, nom_departement, description } = req.body;

        // Check if direction exists (optionnel, selon votre besoin)
        const directionExists = await Direction.findOne({ code_direction: direction });
        if (!directionExists) {
            return res.status(400).json({ message: 'Direction does not exist' });
        }

        // Check if departement already exists in this direction
        const existingDepartement = await Departement.findOne({ 
            direction, 
            code_departement 
        });
        
        if (existingDepartement) {
            return res.status(400).json({ 
                message: 'Departement with this code already exists in this direction' 
            });
        }

        // Create departement
        const departement = await Departement.create({
            direction,
            code_departement,
            nom_departement,
            description,
            created_by: req.user?.id || req.user?.username || 'system'
        });

        res.status(201).json({
            success: true,
            data: departement
        });
    } catch (error) {
        console.error('Create departement error:', error);
        res.status(500).json({ 
            message: 'Error creating departement', 
            error: error.message 
        });
    }
};

// Get all departements
exports.getAllDepartements = async (req, res) => {
    try {
        const { direction } = req.query;
        let query = { is_active: true };
        
        if (direction) {
            query.direction = direction;
        }

        const departements = await Departement.find(query)
            .sort({ created_at: -1 });

        res.json({
            success: true,
            count: departements.length,
            data: departements
        });
    } catch (error) {
        console.error('Get departements error:', error);
        res.status(500).json({ 
            message: 'Error fetching departements', 
            error: error.message 
        });
    }
};

// Get departement by code
exports.getDepartementByCode = async (req, res) => {
    try {
        const departement = await Departement.findOne({ 
            code_departement: req.params.code,
            is_active: true 
        });

        if (!departement) {
            return res.status(404).json({ message: 'Departement not found' });
        }

        res.json({
            success: true,
            data: departement
        });
    } catch (error) {
        console.error('Get departement error:', error);
        res.status(500).json({ 
            message: 'Error fetching departement', 
            error: error.message 
        });
    }
};

// Get departement by ID
exports.getDepartementById = async (req, res) => {
    try {
        const { id } = req.params;

        const departement = await Departement.findOne({
            _id: id,
            is_active: true
        });

        if (!departement) {
            return res.status(404).json({
                success: false,
                message: 'Departement not found'
            });
        }

        res.status(200).json({
            success: true,
            data: departement
        });

    } catch (error) {
        console.error('Get departement by ID error:', error);
        if (error.name === 'CastError') {
            return res.status(400).json({
                success: false,
                message: 'Invalid departement ID'
            });
        }
        res.status(500).json({
            success: false,
            message: 'Error fetching departement',
            error: error.message
        });
    }
};

// Get departements by direction code
exports.getDepartementsByDirectionCode = async (req, res) => {
    try {
        const { directionCode } = req.params;

        const departements = await Departement.find({
            direction: directionCode,
            is_active: true
        }).sort({ created_at: -1 });

        res.json({
            success: true,
            count: departements.length,
            data: departements
        });

    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({
            success: false,
            message: 'Error fetching departements',
            error: error.message
        });
    }
};

// Update departement
exports.updateDepartement = async (req, res) => {
    try {
        const departement = await Departement.findOne({ 
            code_departement: req.params.code 
        });

        if (!departement) {
            return res.status(404).json({ message: 'Departement not found' });
        }

        departement.nom_departement = req.body.nom_departement || departement.nom_departement;
        departement.description = req.body.description || departement.description;
        departement.updated_at = Date.now();

        await departement.save();

        res.json({
            success: true,
            data: departement
        });
    } catch (error) {
        console.error('Update departement error:', error);
        res.status(500).json({ 
            message: 'Error updating departement', 
            error: error.message 
        });
    }
};

// Delete departement (soft delete)
exports.deleteDepartement = async (req, res) => {
    try {
        const departement = await Departement.findOne({ 
            code_departement: req.params.code 
        });

        if (!departement) {
            return res.status(404).json({ message: 'Departement not found' });
        }

        departement.is_active = false;
        departement.updated_at = Date.now();
        await departement.save();

        res.json({
            success: true,
            message: 'Departement deleted successfully'
        });
    } catch (error) {
        console.error('Delete departement error:', error);
        res.status(500).json({ 
            message: 'Error deleting departement', 
            error: error.message 
        });
    }
};

// Hard delete departement
exports.hardDeleteDepartement = async (req, res) => {
    try {
        const departement = await Departement.findOneAndDelete({ 
            code_departement: req.params.code 
        });

        if (!departement) {
            return res.status(404).json({ message: 'Departement not found' });
        }

        res.json({
            success: true,
            message: 'Departement permanently deleted'
        });
    } catch (error) {
        console.error('Hard delete departement error:', error);
        res.status(500).json({ 
            message: 'Error deleting departement', 
            error: error.message 
        });
    }
};
exports.getDepartementsByDirectionId = async (req, res) => {
    try {
        const { directionId } = req.params;

        // D'abord, trouver la direction par son ID pour obtenir son code
        const direction = await Direction.findById(directionId);
        
        if (!direction) {
            return res.status(404).json({
                success: false,
                message: 'Direction not found'
            });
        }

        // Ensuite, trouver les départements qui ont ce code_direction
        const departements = await Departement.find({
            direction: direction.code_direction, // Utiliser le code de la direction trouvée
            is_active: true
        }).sort({ created_at: -1 });

        res.json({
            success: true,
            count: departements.length,
            data: departements,
            direction: direction // Optionnel: retourner aussi les infos de la direction
        });

    } catch (error) {
        console.error('Error:', error);
        res.status(500).json({
            success: false,
            message: 'Error fetching departements by direction ID',
            error: error.message
        });
    }
};