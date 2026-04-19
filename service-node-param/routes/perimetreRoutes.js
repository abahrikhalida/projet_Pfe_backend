const express = require('express');
const router = express.Router();
const { authMiddleware, checkRole } = require('../middleware/auth');
const perimetreController = require('../controllers/perimetreController');

// All routes require authentication
router.use(authMiddleware);

// Routes accessibles à tous les utilisateurs authentifiés
router.get('/', perimetreController.getAllPerimetres);
router.get('/:code', perimetreController.getPerimetreByCode);

// Routes réservées aux chefs (authentifiés)
router.post('/', checkRole(['chef', 'admin']), perimetreController.createPerimetre);
router.put('/:code', checkRole(['chef', 'admin']), perimetreController.updatePerimetre);
router.delete('/:code', checkRole(['chef', 'admin']), perimetreController.deletePerimetre);

module.exports = router;