const express = require('express');
const router = express.Router();
const { authMiddleware, checkRole } = require('../middleware/auth');
const structureController = require('../controllers/structureController');

router.use(authMiddleware);

// Lecture - tous les authentifiés
router.get('/',             structureController.getAllStructures);
router.get('/region/:id',   structureController.getStructuresByRegion);
router.get('/:id',          structureController.getStructureById);

// Écriture - chef/admin uniquement
router.post('/',            checkRole(['chef', 'admin']), structureController.createStructure);
router.put('/:id',          checkRole(['chef', 'admin']), structureController.updateStructure);
router.delete('/:id',       checkRole(['chef', 'admin']), structureController.deleteStructure);

module.exports = router;