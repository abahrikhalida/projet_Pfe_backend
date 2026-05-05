// routes/notificationRoutes.js
const express = require('express');
const router = express.Router();
const notificationController = require('../controllers/notificationController');

// Conversations
router.post('/conversations/direct', notificationController.createDirectConversation);
router.get('/conversations', notificationController.getConversations);
router.get('/conversations/:conversationId', notificationController.getConversation);

// Messages
router.post('/messages', notificationController.sendMessage);
router.get('/messages/:conversationId', notificationController.getMessages);
router.put('/messages/:messageId', notificationController.updateMessage);
router.delete('/messages/:messageId', notificationController.deleteMessage);
router.put('/messages/conversation/:conversationId/read', notificationController.markConversationMessagesAsRead);

// Notifications
router.get('/', notificationController.getNotifications);
router.get('/all', notificationController.getAllNotifications);
router.put('/:id/read', notificationController.markNotificationAsRead);
router.put('/read-all', notificationController.markAllNotificationsAsRead);
router.delete('/:id', notificationController.deleteNotification);

// Utilitaires
router.get('/users', notificationController.getUsers);
router.get('/unread/count', notificationController.getUnreadCount);

module.exports = router;