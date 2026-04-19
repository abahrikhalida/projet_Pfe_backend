const express = require('express');
const router = express.Router();
const { authMiddleware, checkRole } = require('../middleware/auth');
const familleController = require('../controllers/familleController');

// All routes require authentication
router.use(authMiddleware);

// Routes accessibles à tous les utilisateurs authentifiés
router.get('/', familleController.getAllFamilles);
router.get('/:id', familleController.getFamilleById);

// Routes réservées aux chefs (authentifiés)
router.post('/', checkRole(['chef', 'admin']), familleController.createFamille);
router.put('/:id', checkRole(['chef', 'admin']), familleController.updateFamille);
router.delete('/:id', checkRole(['chef', 'admin']), familleController.deleteFamille);

module.exports = router;