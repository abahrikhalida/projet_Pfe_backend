const mongoose = require('mongoose');

const familleDirectionSchema = new mongoose.Schema({
    code_famille: {
        type: String,
        required: [true, 'Code famille is required'],
        unique: true,
        trim: true,
        uppercase: true
    },
    nom_famille: {
        type: String,
        required: [true, 'Nom famille is required'],
        trim: true
    },
    direction: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Direction',
        required: [true, 'Direction is required']
    },
    description: {
        type: String,
        trim: true
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

// Index pour améliorer les recherches
familleDirectionSchema.index({ nom_famille: 1 });
familleDirectionSchema.index({ direction: 1, code_famille: 1 });

module.exports = mongoose.model('FamilleDirection', familleDirectionSchema);