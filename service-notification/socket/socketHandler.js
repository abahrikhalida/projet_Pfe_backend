const Conversation = require('../models/Conversation');
const Message = require('../models/Message');

module.exports = (io) => {
    // Middleware d'authentification socket
    io.use(async (socket, next) => {
        const token = socket.handshake.auth.token;
        if (!token) {
            return next(new Error('Authentication error'));
        }

        try {
            const { authMiddleware } = require('../middleware/auth');
            // Simulation de l'auth pour socket
            const axios = require('axios');
            const response = await axios.get(`${process.env.GATEWAY_URL}/api/verify-token/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            socket.user = response.data.user;
            next();
        } catch (err) {
            next(new Error('Authentication error'));
        }
    });

    io.on('connection', (socket) => {
        console.log(`🔌 User connected: ${socket.user?.id}`);

        // Rejoindre sa room personnelle
        socket.join(`user_${socket.user.id}`);

        // Rejoindre sa room de rôle
        socket.join(`role_${socket.user.role}`);

        // Envoyer un message
        socket.on('send_message', async (data) => {
            try {
                const { conversationId, content } = data;
                
                const conversation = await Conversation.findById(conversationId);
                if (!conversation) return;

                const message = new Message({
                    conversationId,
                    senderId: socket.user.id,
                    senderRole: socket.user.role,
                    senderName: socket.user.nom_complet,
                    content
                });

                await message.save();

                // Mettre à jour la conversation
                conversation.lastMessage = content;
                conversation.lastMessageAt = new Date();
                await conversation.save();

                // Envoyer à tous les participants
                for (const participant of conversation.participants) {
                    io.to(`user_${participant.userId}`).emit('new_message', {
                        conversationId,
                        message,
                        sender: socket.user
                    });
                }
            } catch (err) {
                console.error(err);
                socket.emit('error', { message: err.message });
            }
        });

        // Rejoindre une conversation
        socket.on('join_conversation', async (conversationId) => {
            const conversation = await Conversation.findById(conversationId);
            if (conversation && conversation.participants.some(p => p.userId === socket.user.id)) {
                socket.join(`conv_${conversationId}`);
                socket.emit('joined_conversation', { conversationId });
            }
        });

        // Typing indicator
        socket.on('typing', ({ conversationId, isTyping }) => {
            socket.to(`conv_${conversationId}`).emit('user_typing', {
                userId: socket.user.id,
                name: socket.user.nom_complet,
                isTyping
            });
        });

        socket.on('disconnect', () => {
            console.log(`🔌 User disconnected: ${socket.user?.id}`);
        });
    });
};