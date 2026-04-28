// routes/departementRoutes.js
const express = require('express');
const router = express.Router();
const departementController = require('../controllers/departementController');
const { authMiddleware, checkRole } = require('../middleware/auth');

router.use(authMiddleware);

// Routes principales
router.get('/', departementController.getAllDepartements);
router.get('/by-direction-code/:directionCode', departementController.getDepartementsByDirectionCode);
router.get('/code/:code', departementController.getDepartementByCode);
router.get('/id/:id', departementController.getDepartementById);

// Routes de modification (réservées aux chefs/admin)
router.post('/', checkRole(['chef', 'admin']), departementController.createDepartement);
router.put('/:code', checkRole(['chef', 'admin']), departementController.updateDepartement);
router.delete('/:code', checkRole(['chef', 'admin']), departementController.deleteDepartement);
router.delete('/hard/:code', checkRole(['chef', 'admin']), departementController.hardDeleteDepartement);

module.exports = router;