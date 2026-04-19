const express = require('express');
const router = express.Router();

const { authMiddleware, checkRole } = require('../middleware/auth');
const regionController = require('../controllers/regionController');

// Toutes les routes nécessitent une authentification
router.use(authMiddleware);

// Routes accessibles à tous les utilisateurs authentifiés
router.get('/',     regionController.getAllRegions);
router.get('/:code', regionController.getRegionByCode);

// Routes réservées aux chefs/admins
router.post('/',     checkRole(['chef', 'admin']), regionController.createRegion);
router.put('/:code', checkRole(['chef', 'admin']), regionController.updateRegion);
router.delete('/:code', checkRole(['chef', 'admin']), regionController.deleteRegion);

module.exports = router;