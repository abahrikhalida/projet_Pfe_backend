const mongoose = require('mongoose');

const perimetreSchema = new mongoose.Schema({
    region: {
        type: String,
        required: [true, 'Region is required'],
        ref: 'Region',
        trim: true
    },
    code_perimetre: {
        type: String,
        required: [true, 'Code périmètre is required'],
        unique: true,
        trim: true,
        uppercase: true
    },
    nom_perimetre: {
        type: String,
        required: [true, 'Nom périmètre is required'],
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

// Compound index for region and code_perimetre
perimetreSchema.index({ region: 1, code_perimetre: 1 }, { unique: true });
perimetreSchema.index({ nom_perimetre: 1 });

module.exports = mongoose.model('Perimetre', perimetreSchema);