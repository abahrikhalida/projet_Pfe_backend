const mongoose = require('mongoose');

const structureSchema = new mongoose.Schema({
    code_structure: {
        type: String,
        required: [true, 'Code structure is required'],
        unique: true,
        trim: true,
        uppercase: true
    },
    type_structure: {
        type: String,
        // required: [true, 'Type structure is required'],
        trim: true,
        uppercase: true
    },
    nom_structure: {
        type: String,
        required: [true, 'Nom structure is required'],
        trim: true
    },
    description: {
        type: String,
        trim: true
    },
    region: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Region',
        required: [true, 'Region is required']
    },
    created_by: {
        type: String,
        required: true
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

structureSchema.index({ region: 1 });
structureSchema.index({ type_structure: 1, region: 1 }, { unique: true });

module.exports = mongoose.model('Structure', structureSchema);