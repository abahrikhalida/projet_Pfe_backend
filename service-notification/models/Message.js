// models/Message.js
const mongoose = require('mongoose');

const messageSchema = new mongoose.Schema({
    conversationId: { type: mongoose.Schema.Types.ObjectId, ref: 'Conversation', required: true },
    senderId: { type: String, required: true },
    senderRole: { type: String, required: true },
    senderName: { type: String },
    content: { type: String, required: true },
    readBy: [{
        userId: String,
        readAt: { type: Date, default: Date.now }
    }],
    isDeleted: { type: Boolean, default: false },
    createdAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Message', messageSchema);