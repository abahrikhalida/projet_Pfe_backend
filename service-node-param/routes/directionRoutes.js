const express = require('express');
const router = express.Router();
const {
    createDirection,
    getAllDirections,
    getDirectionById,
    getDirectionByCode,
    updateDirection,
    deleteDirection,
    hardDeleteDirection
} = require('../controllers/DirectionController');

router.post('/', createDirection);
router.get('/', getAllDirections);
router.get('/:id', getDirectionById);
router.get('/code/:code', getDirectionByCode);
router.put('/:id', updateDirection);
router.delete('/:id', deleteDirection);
router.delete('/hard/:id', hardDeleteDirection);

module.exports = router;