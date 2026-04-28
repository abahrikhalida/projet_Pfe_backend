// const Famille = require('../models/Famille');
// const Region = require('../models/Region');
// const Perimetre = require('../models/Perimetre');
// const mongoose = require('mongoose');

// // @desc    Create new famille
// // @route   POST /api/familles
// // @access  Private (Chef only)
// exports.createFamille = async (req, res) => {
//     try {
//         const { region, perimetre, champs, code_famille, nom_famille, description } = req.body;

//         // Check if region exists
//         const regionExists = await Region.findOne({ code_region: region });
//         if (!regionExists) {
//             return res.status(400).json({ message: 'Region does not exist' });
//         }

//         // Check if perimetre exists in this region
//         const perimetreExists = await Perimetre.findOne({ 
//             region, 
//             code_perimetre: perimetre 
//         });
        
//         if (!perimetreExists) {
//             return res.status(400).json({ 
//                 message: 'Perimetre does not exist in this region' 
//             });
//         }

//         // Check if famille already exists
//         const existingFamille = await Famille.findOne({ 
//             region, 
//             perimetre, 
//             champs, 
//             code_famille 
//         });
        
//         if (existingFamille) {
//             return res.status(400).json({ 
//                 message: 'Famille with these parameters already exists' 
//             });
//         }

//         // Create famille
//         const famille = await Famille.create({
//             region,
//             perimetre,
//             champs,
//             code_famille,
//             nom_famille,
//             description,
//             created_by: req.user.id || req.user.username
//         });

//         res.status(201).json({
//             success: true,
//             data: famille
//         });
//     } catch (error) {
//         console.error('Create famille error:', error);
//         res.status(500).json({ 
//             message: 'Error creating famille', 
//             error: error.message 
//         });
//     }
// };

// // @desc    Get all familles
// // @route   GET /api/familles
// // @access  Private
// exports.getAllFamilles = async (req, res) => {
//     try {
//         const { region, perimetre, champs } = req.query;
//         let query = { is_active: true };
        
//         if (region) query.region = region;
//         if (perimetre) query.perimetre = perimetre;
//         if (champs) query.champs = champs;

//         const familles = await Famille.find(query)
//             .sort({ created_at: -1 });

//         res.json({
//             success: true,
//             count: familles.length,
//             data: familles
//         });
//     } catch (error) {
//         console.error('Get familles error:', error);
//         res.status(500).json({ 
//             message: 'Error fetching familles', 
//             error: error.message 
//         });
//     }
// };

// // @desc    Get famille by id
// // @route   GET /api/familles/:id
// // @access  Private
// exports.getFamilleById = async (req, res) => {
//     try {
//         const famille = await Famille.findById(req.params.id);

//         if (!famille || !famille.is_active) {
//             return res.status(404).json({ message: 'Famille not found' });
//         }

//         res.json({
//             success: true,
//             data: famille
//         });
//     } catch (error) {
//         console.error('Get famille error:', error);
//         res.status(500).json({ 
//             message: 'Error fetching famille', 
//             error: error.message 
//         });
//     }
// };

// // @desc    Update famille
// // @route   PUT /api/familles/:id
// // @access  Private (Chef only)
// exports.updateFamille = async (req, res) => {
//     try {
//         const famille = await Famille.findById(req.params.id);

//         if (!famille) {
//             return res.status(404).json({ message: 'Famille not found' });
//         }

//         // Update fields
//         famille.nom_famille = req.body.nom_famille || famille.nom_famille;
//         famille.description = req.body.description || famille.description;
//         famille.updated_at = Date.now();

//         await famille.save();

//         res.json({
//             success: true,
//             data: famille
//         });
//     } catch (error) {
//         console.error('Update famille error:', error);
//         res.status(500).json({ 
//             message: 'Error updating famille', 
//             error: error.message 
//         });
//     }
// };

// // @desc    Delete famille (soft delete)
// // @route   DELETE /api/familles/:id
// // @access  Private (Chef only)
// exports.deleteFamille = async (req, res) => {
//     try {
//         const famille = await Famille.findById(req.params.id);

//         if (!famille) {
//             return res.status(404).json({ message: 'Famille not found' });
//         }

//         famille.is_active = false;
//         famille.updated_at = Date.now();
//         await famille.save();

//         res.json({
//             success: true,
//             message: 'Famille deleted successfully'
//         });
//     } catch (error) {
//         console.error('Delete famille error:', error);
//         res.status(500).json({ 
//             message: 'Error deleting famille', 
//             error: error.message 
//         });
//     }
// };
// // @desc    Get familles by region ObjectId and perimetre code
// // @route   GET /api/familles/region/:regionId/perimetre/:perimetreCode
// // @access  Private
// exports.getFamillesByRegionIdAndPerimetre = async (req, res) => {
//     try {
//         const { regionId, perimetreCode } = req.params;
        
//         console.log("=== DEBUG getFamillesByRegionIdAndPerimetre ===");
//         console.log("regionId reçu:", regionId);
//         console.log("perimetreCode reçu:", perimetreCode);
        
//         // Vérifier si l'ID de région est valide
//         const isValidObjectId = mongoose.Types.ObjectId.isValid(regionId);
//         if (!isValidObjectId) {
//             return res.status(400).json({
//                 success: false,
//                 message: 'ID de région invalide'
//             });
//         }
        
//         // 1. Trouver la région par son ObjectId
//         const region = await Region.findById(regionId);
//         if (!region) {
//             return res.status(404).json({
//                 success: false,
//                 message: 'Région non trouvée'
//             });
//         }
        
//         console.log("Code région trouvé:", region.code_region);
        
//         // 2. Récupérer les familles avec le code_region et le perimetre
//         const familles = await Famille.find({ 
//             region: region.code_region,
//             perimetre: perimetreCode,
//             is_active: true 
//         }).sort({ created_at: -1 });
        
//         console.log("Nombre de familles trouvées:", familles.length);
        
//         res.json({
//             success: true,
//             count: familles.length,
//             data: familles
//         });
        
//     } catch (error) {
//         console.error('Get familles by region ID error:', error);
//         res.status(500).json({ 
//             success: false,
//             message: 'Error fetching familles', 
//             error: error.message 
//         });
//     }
// };
// // @desc    Get famille by code_famille
// // @route   GET /api/familles/by-code/:code
// // @access  Private
// exports.getFamilleByCode = async (req, res) => {
//     try {
//         const { code } = req.params;

//         const famille = await Famille.findOne({
//             code_famille: code,
//             is_active: true
//         });

//         if (!famille) {
//             return res.status(404).json({
//                 success: false,
//                 message: 'Famille not found'
//             });
//         }

//         res.json({
//             success: true,
//             data: famille
//         });

//     } catch (error) {
//         console.error('Get famille by code error:', error);
//         res.status(500).json({
//             success: false,
//             message: 'Error fetching famille',
//             error: error.message
//         });
//     }
// };
// // @desc Get familles by code_region & code_perimetre
// // @route GET /api/familles/by-region-perimetre/:codeRegion/:codePerimetre
// // @access Private
// // exports.getFamillesByCodeRegionAndPerimetre = async (req, res) => {
// //     try {
// //         const { codeRegion, codePerimetre } = req.params;

// //         // vérifier région
// //         const region = await Region.findOne({ code_region: codeRegion });
// //         if (!region) {
// //             return res.status(404).json({
// //                 success: false,
// //                 message: 'Region not found'
// //             });
// //         }

// //         // vérifier périmètre
// //         const perimetre = await Perimetre.findOne({
// //             region: codeRegion,
// //             code_perimetre: codePerimetre
// //         });

// //         if (!perimetre) {
// //             return res.status(404).json({
// //                 success: false,
// //                 message: 'Perimetre not found in this region'
// //             });
// //         }

// //         // récupérer familles
// //         const familles = await Famille.find({
// //             region: codeRegion,
// //             perimetre: codePerimetre,
// //             is_active: true
// //         }).sort({ created_at: -1 });

// //         res.json({
// //             success: true,
// //             count: familles.length,
// //             data: familles
// //         });

// //     } catch (error) {
// //         console.error('Get familles error:', error);
// //         res.status(500).json({
// //             success: false,
// //             message: 'Error fetching familles',
// //             error: error.message
// //         });
// //     }
// // };
// exports.getFamillesByFilter = async (req, res) => {
//     try {
//         const { codeRegion, codePerimetre } = req.params;

//         const familles = await Famille.find({
//             region: codeRegion,
//             perimetre: codePerimetre,
//             is_active: true
//         }).sort({ created_at: -1 });

//         res.json({
//             success: true,
//             count: familles.length,
//             data: familles
//         });

//     } catch (error) {
//         console.error('Error:', error);
//         res.status(500).json({
//             success: false,
//             message: 'Error fetching familles',
//             error: error.message
//         });
//     }
// };
const Famille = require('../models/Famille');

// @desc    Create new famille
// @route   POST /api/familles
// @access  Private
exports.createFamille = async (req, res) => {
    try {
        const { code_famille, nom_famille, description } = req.body;

        // Check if famille already exists
        const existingFamille = await Famille.findOne({ code_famille });
        
        if (existingFamille) {
            return res.status(400).json({ 
                success: false,
                message: 'Ce code famille existe déjà' 
            });
        }

        // Create famille
        const famille = await Famille.create({
            code_famille,
            nom_famille,
            description: description || '',
            created_by: req.user.id || req.user.username
        });

        res.status(201).json({
            success: true,
            data: famille
        });
    } catch (error) {
        console.error('Create famille error:', error);
        res.status(500).json({ 
            success: false,
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
        const familles = await Famille.find({ is_active: true })
            .sort({ code_famille: 1 });

        res.json({
            success: true,
            count: familles.length,
            data: familles
        });
    } catch (error) {
        console.error('Get familles error:', error);
        res.status(500).json({ 
            success: false,
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
            return res.status(404).json({ 
                success: false,
                message: 'Famille not found' 
            });
        }

        res.json({
            success: true,
            data: famille
        });
    } catch (error) {
        console.error('Get famille error:', error);
        res.status(500).json({ 
            success: false,
            message: 'Error fetching famille', 
            error: error.message 
        });
    }
};

// @desc    Get famille by code
// @route   GET /api/familles/by-code/:code
// @access  Private
exports.getFamilleByCode = async (req, res) => {
    try {
        const famille = await Famille.findOne({ 
            code_famille: req.params.code, 
            is_active: true 
        });

        if (!famille) {
            return res.status(404).json({ 
                success: false,
                message: 'Famille not found' 
            });
        }

        res.json({
            success: true,
            data: famille
        });
    } catch (error) {
        console.error('Get famille by code error:', error);
        res.status(500).json({ 
            success: false,
            message: 'Error fetching famille', 
            error: error.message 
        });
    }
};

// @desc    Update famille
// @route   PUT /api/familles/:id
// @access  Private
exports.updateFamille = async (req, res) => {
    try {
        const { nom_famille, description } = req.body;

        const famille = await Famille.findById(req.params.id);

        if (!famille) {
            return res.status(404).json({ 
                success: false,
                message: 'Famille not found' 
            });
        }

        // Update fields
        if (nom_famille) famille.nom_famille = nom_famille;
        if (description !== undefined) famille.description = description;
        famille.updated_at = Date.now();

        await famille.save();

        res.json({
            success: true,
            data: famille
        });
    } catch (error) {
        console.error('Update famille error:', error);
        res.status(500).json({ 
            success: false,
            message: 'Error updating famille', 
            error: error.message 
        });
    }
};

// @desc    Delete famille (soft delete)
// @route   DELETE /api/familles/:id
// @access  Private
exports.deleteFamille = async (req, res) => {
    try {
        const famille = await Famille.findById(req.params.id);

        if (!famille) {
            return res.status(404).json({ 
                success: false,
                message: 'Famille not found' 
            });
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
            success: false,
            message: 'Error deleting famille', 
            error: error.message 
        });
    }
};

// @desc    Hard delete famille (permanent)
// @route   DELETE /api/familles/:id/permanent
// @access  Private (Admin only)
exports.hardDeleteFamille = async (req, res) => {
    try {
        const famille = await Famille.findByIdAndDelete(req.params.id);

        if (!famille) {
            return res.status(404).json({ 
                success: false,
                message: 'Famille not found' 
            });
        }

        res.json({
            success: true,
            message: 'Famille permanently deleted'
        });
    } catch (error) {
        console.error('Hard delete famille error:', error);
        res.status(500).json({ 
            success: false,
            message: 'Error deleting famille', 
            error: error.message 
        });
    }
};