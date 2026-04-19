const mongoose = require('mongoose');

const regionSchema = new mongoose.Schema({
    code_region: {
        type: String,
        required: [true, 'Code région is required'],
        unique: true,        // ← Index unique automatique
        trim: true,
        uppercase: true
    },
    nom_region: {
        type: String,
        required: [true, 'Nom région is required'],
        trim: true
    },
    description: {
        type: String,
        trim: true
    },
    created_by: {
        type: String,
        required: true
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

// Index pour améliorer les recherches par nom (optionnel mais utile)
regionSchema.index({ nom_region: 1 });

module.exports = mongoose.model('Region', regionSchema);