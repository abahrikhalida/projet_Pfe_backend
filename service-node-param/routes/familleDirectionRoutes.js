const express = require('express');
const router = express.Router();
const {
    createFamilleDirection,
    getAllFamillesDirection,
    getFamillesByDirection,
    getFamilleDirectionById,
    getFamilleDirectionByCode,
    updateFamilleDirection,
    deleteFamilleDirection,
    hardDeleteFamilleDirection
} = require('../controllers/familleDirectionController');

router.post('/', createFamilleDirection);
router.get('/', getAllFamillesDirection);
router.get('/direction/:directionId', getFamillesByDirection);
router.get('/:id', getFamilleDirectionById);
router.get('/code/:code', getFamilleDirectionByCode);
router.put('/:id', updateFamilleDirection);
router.delete('/:id', deleteFamilleDirection);
router.delete('/hard/:id', hardDeleteFamilleDirection);

module.exports = router;