// const mongoose = require('mongoose');

// const familleSchema = new mongoose.Schema({
//     region: {
//         type: String,
//         required: [true, 'Region is required'],
//         ref: 'Region',
//         trim: true
//     },
//     perimetre: {
//         type: String,
//         required: [true, 'Périmètre is required'],
//         ref: 'Perimetre',
//         trim: true
//     },
//     champs: {
//         type: String,
//         required: [true, 'Champs is required'],
//         trim: true
//     },
//     code_famille: {
//         type: String,
//         required: [true, 'Code famille is required'],
//         trim: true,
//         uppercase: true
//     },
//     nom_famille: {
//         type: String,
//         required: [true, 'Nom famille is required'],
//         trim: true
//     },
//     description: {
//         type: String,
//         trim: true
//     },
//     created_by: {
//         type: String,
//         required: true
//     },
//     created_at: {
//         type: Date,
//         default: Date.now
//     },
//     updated_at: {
//         type: Date,
//         default: Date.now
//     },
//     is_active: {
//         type: Boolean,
//         default: true
//     }
// }, {
//     timestamps: { 
//         createdAt: 'created_at', 
//         updatedAt: 'updated_at' 
//     }
// });

// // Compound index for region, perimetre, champs, code_famille
// familleSchema.index({ 
//     region: 1, 
//     perimetre: 1, 
//     champs: 1, 
//     code_famille: 1 
// }, { unique: true });

// familleSchema.index({ nom_famille: 1 });

// module.exports = mongoose.model('Famille', familleSchema);
const mongoose = require('mongoose');

const familleSchema = new mongoose.Schema({
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

// Index pour code_famille unique
familleSchema.index({ code_famille: 1 }, { unique: true });
familleSchema.index({ nom_famille: 1 });

module.exports = mongoose.model('Famille', familleSchema);