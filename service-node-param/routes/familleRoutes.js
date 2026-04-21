const express = require('express');
const router = express.Router();
const { authMiddleware, checkRole } = require('../middleware/auth');
const familleController = require('../controllers/familleController');

// All routes require authentication
router.use(authMiddleware);
router.get('/region/:regionId/perimetre/:perimetreCode', familleController.getFamillesByRegionIdAndPerimetre);
// GET /api/familles/by-region-perimetre/:codeRegion/:codePerimetre
router.get('/by-region-perimetre/:codeRegion/:codePerimetre', familleController.getFamillesByFilter);
// Routes accessibles à tous les utilisateurs authentifiés
router.get('/', familleController.getAllFamilles);
router.get('/:id', familleController.getFamilleById);
router.get('/by-code/:code', familleController.getFamilleByCode);

// Routes réservées aux chefs (authentifiés)
router.post('/', checkRole(['chef', 'admin']), familleController.createFamille);
router.put('/:id', checkRole(['chef', 'admin']), familleController.updateFamille);
router.delete('/:id', checkRole(['chef', 'admin']), familleController.deleteFamille);

module.exports = router;