// models/Departement.js
const mongoose = require('mongoose');

const departementSchema = new mongoose.Schema({
    code_departement: {
        type: String,
        required: [true, 'Code département is required'],
        unique: true,
        trim: true,
        uppercase: true
    },
    nom_departement: {
        type: String,
        required: [true, 'Nom département is required'],
        trim: true
    },
    direction: {
        type: String,  // ← Changer de ObjectId à String (comme region dans Perimetre)
        required: [true, 'Direction is required']
    },
    description: {
        type: String,
        default: ''
    },
    created_by: {
        type: String,
        default: 'system'
    },
    created_at: {
        type: Date,
        default: Date.now
    },
    updated_at: {
        type: Date,
        default: Date.now
    },
    is_active: {
        type: Boolean,
        default: true
    }
}, {
    timestamps: { 
        createdAt: 'created_at', 
        updatedAt: 'updated_at' 
    }
});

departementSchema.index({ nom_departement: 1 });
departementSchema.index({ direction: 1, code_departement: 1 });

module.exports = mongoose.model('Departement', departementSchema);