// models/Direction.js
const mongoose = require('mongoose');

const directionSchema = new mongoose.Schema({
    code_direction: {
        type: String,
        required: [true, 'Code direction is required'],
        unique: true,
        trim: true,
        uppercase: true
    },
    nom_direction: {
        type: String,
        required: [true, 'Nom direction is required'],
        trim: true
    },
//    created_by: {
//     type: String,
//     default: 'system' // Valeur par défaut
   
// },
    // created_by: {
    //     type: String,
    //     required: true
    // },
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

directionSchema.index({ nom_direction: 1 });

module.exports = mongoose.model('Direction', directionSchema);