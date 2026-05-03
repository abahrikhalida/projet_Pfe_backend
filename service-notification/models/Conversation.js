// models/Conversation.js
const mongoose = require('mongoose');

const conversationSchema = new mongoose.Schema({
    participants: [{
        userId: { type: String, required: true },
        role: { type: String, required: true },
        nom_complet: { type: String }
    }],
    type: {
        type: String,
        enum: ['direct', 'group', 'role_based'],
        default: 'direct'
    },
    subject: { type: String },
    lastMessage: { type: String },
    lastMessageAt: { type: Date, default: Date.now },
    createdBy: { type: String },
    createdAt: { type: Date, default: Date.now },
    updatedAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Conversation', conversationSchema);