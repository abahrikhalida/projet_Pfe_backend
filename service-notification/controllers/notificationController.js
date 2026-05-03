// controllers/notificationController.js
const Conversation = require('../models/Conversation');
const Message = require('../models/Message');
const axios = require('axios');

// ==================== CONVERSATIONS ====================

// Créer une conversation directe entre deux utilisateurs
exports.createDirectConversation = async (req, res) => {
    try {
        const { targetUserId, targetUserRole, targetUserName } = req.body;
        const currentUser = req.user;

        if (!targetUserId) {
            return res.status(400).json({ error: 'targetUserId est requis' });
        }

        const existing = await Conversation.findOne({
            type: 'direct',
            'participants.userId': { $all: [currentUser.id, targetUserId] }
        });

        if (existing) {
            return res.json(existing);
        }

        const participants = [
            { 
                userId: currentUser.id, 
                role: currentUser.role, 
                nom_complet: currentUser.nom_complet || currentUser.username 
            },
            { 
                userId: targetUserId, 
                role: targetUserRole, 
                nom_complet: targetUserName || targetUserRole 
            }
        ];

        const conversation = new Conversation({
            participants,
            type: 'direct',
            subject: `Conversation entre ${currentUser.nom_complet} et ${targetUserName}`,
            lastMessageAt: new Date(),
            createdBy: currentUser.id
        });

        await conversation.save();
        res.status(201).json(conversation);
    } catch (err) {
        console.error('Erreur createDirectConversation:', err);
        res.status(500).json({ error: err.message });
    }
};

// Récupérer toutes les conversations de l'utilisateur
exports.getConversations = async (req, res) => {
    try {
        const userId = req.user.id;
        const conversations = await Conversation.find({
            'participants.userId': userId
        }).sort({ lastMessageAt: -1 });
        res.json(conversations || []);
    } catch (err) {
        console.error('Erreur getConversations:', err);
        res.status(500).json({ error: err.message });
    }
};

// Récupérer une conversation spécifique
exports.getConversation = async (req, res) => {
    try {
        const { conversationId } = req.params;
        const currentUser = req.user;

        const conversation = await Conversation.findById(conversationId);
        if (!conversation) {
            return res.status(404).json({ error: 'Conversation non trouvée' });
        }

        if (!conversation.participants.some(p => p.userId === currentUser.id)) {
            return res.status(403).json({ error: 'Accès refusé' });
        }

        res.json(conversation);
    } catch (err) {
        console.error('Erreur getConversation:', err);
        res.status(500).json({ error: err.message });
    }
};

// ==================== MESSAGES ====================

// Envoyer un message
exports.sendMessage = async (req, res) => {
    try {
        const { conversationId, content } = req.body;
        const currentUser = req.user;

        if (!conversationId || !content) {
            return res.status(400).json({ error: 'conversationId et content sont requis' });
        }

        const conversation = await Conversation.findById(conversationId);
        if (!conversation) {
            return res.status(404).json({ error: 'Conversation non trouvée' });
        }

        if (!conversation.participants.some(p => p.userId === currentUser.id)) {
            return res.status(403).json({ error: 'Accès refusé' });
        }

        const message = new Message({
            conversationId,
            senderId: currentUser.id,
            senderRole: currentUser.role,
            senderName: currentUser.nom_complet || currentUser.username,
            content
        });

        await message.save();

        conversation.lastMessage = content;
        conversation.lastMessageAt = new Date();
        await conversation.save();

        res.status(201).json(message);
    } catch (err) {
        console.error('Erreur sendMessage:', err);
        res.status(500).json({ error: err.message });
    }
};

// Récupérer les messages d'une conversation
exports.getMessages = async (req, res) => {
    try {
        const { conversationId } = req.params;
        const { page = 1, limit = 50 } = req.query;
        const currentUser = req.user;

        const conversation = await Conversation.findById(conversationId);
        if (!conversation) {
            return res.status(404).json({ error: 'Conversation non trouvée' });
        }

        if (!conversation.participants.some(p => p.userId === currentUser.id)) {
            return res.status(403).json({ error: 'Accès refusé' });
        }

        const messages = await Message.find({ conversationId, isDeleted: false })
            .sort({ createdAt: -1 })
            .skip((page - 1) * limit)
            .limit(limit);

        await Message.updateMany(
            { conversationId, 'readBy.userId': { $ne: currentUser.id } },
            { $push: { readBy: { userId: currentUser.id, readAt: new Date() } } }
        );

        res.json({
            messages: messages.reverse(),
            page,
            limit,
            total: await Message.countDocuments({ conversationId, isDeleted: false })
        });
    } catch (err) {
        console.error('Erreur getMessages:', err);
        res.status(500).json({ error: err.message });
    }
};

// ==================== NOTIFICATIONS ====================

// Récupérer les notifications de l'utilisateur
exports.getNotifications = async (req, res) => {
    try {
        const notifications = [
            {
                id: '1',
                title: 'Projet validé',
                message: 'Le projet a été validé',
                type: 'validation',
                read: false,
                created_at: new Date()
            }
        ];
        res.json({ notifications, unread_count: notifications.filter(n => !n.read).length });
    } catch (err) {
        console.error('Erreur getNotifications:', err);
        res.status(500).json({ error: err.message });
    }
};

// Récupérer toutes les notifications
exports.getAllNotifications = async (req, res) => {
    try {
        const notifications = [
            {
                id: '1',
                title: 'Projet validé',
                message: 'Le projet a été validé',
                type: 'validation',
                read: false,
                created_at: new Date()
            }
        ];
        res.json({ notifications });
    } catch (err) {
        console.error('Erreur getAllNotifications:', err);
        res.status(500).json({ error: err.message });
    }
};

// Marquer une notification comme lue
exports.markNotificationAsRead = async (req, res) => {
    try {
        const { id } = req.params;
        res.json({ success: true });
    } catch (err) {
        console.error('Erreur markNotificationAsRead:', err);
        res.status(500).json({ error: err.message });
    }
};

// Marquer toutes les notifications comme lues
exports.markAllNotificationsAsRead = async (req, res) => {
    try {
        res.json({ success: true });
    } catch (err) {
        console.error('Erreur markAllNotificationsAsRead:', err);
        res.status(500).json({ error: err.message });
    }
};

// Supprimer une notification
exports.deleteNotification = async (req, res) => {
    try {
        const { id } = req.params;
        res.json({ success: true });
    } catch (err) {
        console.error('Erreur deleteNotification:', err);
        res.status(500).json({ error: err.message });
    }
};

// ==================== UTILITAIRES ====================

// Compter les messages non lus
exports.getUnreadCount = async (req, res) => {
    try {
        const currentUser = req.user;
        const conversations = await Conversation.find({
            'participants.userId': currentUser.id
        });
        const conversationIds = conversations.map(c => c._id);
        const unreadCount = await Message.countDocuments({
            conversationId: { $in: conversationIds },
            'readBy.userId': { $ne: currentUser.id },
            senderId: { $ne: currentUser.id }
        });
        res.json({ unreadCount });
    } catch (err) {
        console.error('Erreur getUnreadCount:', err);
        res.status(500).json({ error: err.message });
    }
};

// Récupérer tous les utilisateurs
exports.getUsers = async (req, res) => {
    try {
        const token = req.headers.authorization;
        const response = await axios.get(`${process.env.GATEWAY_URL}/api/users/`, {
            headers: { Authorization: token }
        });
        const users = response.data.users || response.data || [];
        res.json({ users });
    } catch (err) {
        console.error('Erreur getUsers:', err);
        res.status(500).json({ error: err.message });
    }
};

// controllers/notificationController.js

/**
 * Marquer tous les messages d'une conversation comme lus
 */
exports.markConversationMessagesAsRead = async (req, res) => {
    try {
        const { conversationId } = req.params;
        const userId = req.user.id;

        const Conversation = require('../models/Conversation');
        const Message = require('../models/Message');

        const conversation = await Conversation.findById(conversationId);
        if (!conversation) {
            return res.status(404).json({ message: 'Conversation non trouvée' });
        }

        const isParticipant = conversation.participants.some(
            p => p.userId.toString() === userId
        );

        if (!isParticipant) {
            return res.status(403).json({ message: 'Accès non autorisé à cette conversation' });
        }

        await Message.updateMany(
            {
                conversationId: conversationId,
                'readBy.userId': { $ne: userId },
                senderId: { $ne: userId }
            },
            {
                $addToSet: {
                    readBy: {
                        userId: userId,
                        readAt: new Date()
                    }
                }
            }
        );

        // Mettre à jour le compteur global
        const totalUnread = await Message.countDocuments({
            'readBy.userId': { $ne: userId },
            senderId: { $ne: userId }
        });

        res.status(200).json({ 
            message: 'Messages marqués comme lus avec succès',
            conversationId: conversationId,
            totalUnread: totalUnread
        });
    } catch (error) {
        console.error('Erreur lors du marquage:', error);
        res.status(500).json({ message: 'Erreur serveur', error: error.message });
    }
};

/**
 * Modifier un message
 */
exports.updateMessage = async (req, res) => {
    try {
        const { messageId } = req.params;
        const { content } = req.body;
        const userId = req.user.id;

        const Message = require('../models/Message');

        const message = await Message.findById(messageId);
        
        if (!message) {
            return res.status(404).json({ message: 'Message non trouvé' });
        }

        if (message.senderId.toString() !== userId) {
            return res.status(403).json({ message: 'Vous ne pouvez modifier que vos propres messages' });
        }

        const messageAge = Date.now() - new Date(message.createdAt).getTime();
        const maxAgeForEdit = 5 * 60 * 1000; // 5 minutes
        
        if (messageAge > maxAgeForEdit) {
            return res.status(403).json({ message: 'Les messages ne peuvent être modifiés que dans les 5 minutes' });
        }

        message.content = content;
        await message.save();

        res.status(200).json(message);
    } catch (error) {
        console.error('Erreur modification:', error);
        res.status(500).json({ message: 'Erreur serveur', error: error.message });
    }
};

/**
 * Supprimer un message
 */
exports.deleteMessage = async (req, res) => {
    try {
        const { messageId } = req.params;
        const userId = req.user.id;
        const userRole = req.user.role;

        const Message = require('../models/Message');
        const Conversation = require('../models/Conversation');

        const message = await Message.findById(messageId);
        
        if (!message) {
            return res.status(404).json({ message: 'Message non trouvé' });
        }

        const conversation = await Conversation.findById(message.conversationId);
        
        let isAuthorized = false;
        
        if (message.senderId.toString() === userId) {
            isAuthorized = true;
        }
        
        if (userRole === 'admin' || userRole === 'super_admin') {
            isAuthorized = true;
        }
        
        if (!isAuthorized) {
            return res.status(403).json({ message: 'Non autorisé' });
        }

        await Message.findByIdAndDelete(messageId);

        const lastMessage = await Message.findOne({ conversationId: message.conversationId })
            .sort({ createdAt: -1 })
            .limit(1);

        if (lastMessage) {
            conversation.lastMessage = lastMessage.content;
            conversation.lastMessageAt = lastMessage.createdAt;
        } else {
            conversation.lastMessage = null;
            conversation.lastMessageAt = null;
        }
        
        await conversation.save();

        res.status(200).json({ 
            message: 'Message supprimé',
            messageId: messageId
        });
    } catch (error) {
        console.error('Erreur suppression:', error);
        res.status(500).json({ message: 'Erreur serveur', error: error.message });
    }
};

/**
 * Compter les messages non lus par conversation
 */
exports.getUnreadCountsByConversation = async (req, res) => {
    try {
        const userId = req.user.id;
        
        const Conversation = require('../models/Conversation');
        const Message = require('../models/Message');
        
        const conversations = await Conversation.find({
            'participants.userId': userId
        });
        
        const counts = {};
        
        for (const conv of conversations) {
            const unreadCount = await Message.countDocuments({
                conversationId: conv._id,
                senderId: { $ne: userId },
                'readBy.userId': { $ne: userId }
            });
            counts[conv._id] = unreadCount;
        }
        
        res.json({ counts });
    } catch (error) {
        res.status(500).json({ message: error.message });
    }
};