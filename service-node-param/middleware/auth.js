// middleware/auth.js — VERSION FINALE
//
// Flux :
//  1. jwt.verify(token, SECRET_KEY)  →  vérifie signature + expiry LOCALEMENT (0 réseau)
//  2. Cache hit ?                    →  retour immédiat (0 réseau)
//  3. GET /api/users/<id>/           →  1 seul appel pour récupérer role, nom, email
//
// .env requis :
//   JWT_SECRET=<valeur exacte de SECRET_KEY dans settings.py Django>
//   AUTH_SERVICE_URL=http://127.0.0.1:8000/api

const axios = require('axios');
const jwt   = require('jsonwebtoken');

// ── Config ───────────────────────────────────────────────────
const CONFIG = {
    AUTH_URL:   process.env.AUTH_SERVICE_URL || 'http://127.0.0.1:8000/api',
    JWT_SECRET: process.env.JWT_SECRET,          // même valeur que SECRET_KEY Django
    CACHE_TTL:  10 * 60 * 1000,                  // 10 minutes
    TIMEOUT:    5000,
};

// ── Cache mémoire ────────────────────────────────────────────
const _cache = new Map();

function cacheGet(key) {
    const item = _cache.get(key);
    if (!item) return null;
    if (Date.now() > item.exp) { _cache.delete(key); return null; }
    return item.data;
}

function cacheSet(key, data) {
    _cache.set(key, { data, exp: Date.now() + CONFIG.CACHE_TTL });
}

// ── Étape 1 : vérifier JWT localement ───────────────────────
// Django SimpleJWT utilise HS256 + SECRET_KEY → on peut vérifier sans appel réseau
// Retourne le payload décodé ou null si invalide/expiré
function verifyLocal(token) {
    if (!CONFIG.JWT_SECRET) {
        console.error('❌ JWT_SECRET non défini dans .env !');
        return null;
    }
    try {
        const payload = jwt.verify(token, CONFIG.JWT_SECRET, { algorithms: ['HS256'] });

        // Vérifier que c'est un access token (pas un refresh)
        if (payload.token_type !== 'access') {
            console.log('❌ Token de type:', payload.token_type, '— access token requis');
            return null;
        }

        console.log(`✅ JWT valide — user_id: ${payload.user_id}`);
        return payload;

    } catch (err) {
        // TokenExpiredError, JsonWebTokenError, etc.
        console.log(`❌ JWT invalide: ${err.message}`);
        return null;
    }
}

// ── Étape 2 : récupérer les données user depuis Django ───────
// GET /api/users/<id>/  →  { id, role, nom_complet, email, is_staff, ... }
async function fetchUserFromDjango(userId, token) {
    try {
        const res = await axios.get(
            `${CONFIG.AUTH_URL}/users/${userId}/`,
            {
                headers: { Authorization: `Bearer ${token}` },
                timeout: CONFIG.TIMEOUT
            }
        );
        console.log(`✅ /users/${userId}/ →`, { role: res.data?.role, email: res.data?.email });
        return res.data;
    } catch (err) {
        const status = err.response?.status;
        const detail = err.response?.data?.detail || err.message;
        console.log(`❌ /users/${userId}/ échoué: ${status} — ${detail}`);
        return null;
    }
}

// ── Résolution principale ────────────────────────────────────
async function resolveUser(token) {

    // 1. Vérification locale (signature + expiry)
    const payload = verifyLocal(token);
    if (!payload) return null;

    const userId   = payload.user_id.toString();
    const cacheKey = `user:${userId}`;

    // 2. Cache
    const cached = cacheGet(cacheKey);
    if (cached) {
        console.log(`📦 Cache hit — user ${userId}`);
        return cached;
    }

    // 3. 1 appel Django pour récupérer le rôle
    const data = await fetchUserFromDjango(userId, token);

    // Construire l'objet user
    // api_get_user retourne: { id, email, nom_complet, role, photo_profil, is_staff, is_superuser }
    const user = {
        id:          userId,
        role:        data?.role || (data?.is_staff ? 'admin' : 'user'),
        username:    data?.email || `user_${userId}`,
        nom_complet: data?.nom_complet || null,
        email:       data?.email || null,
        is_staff:    data?.is_staff || false,
    };

    console.log(`✅ User résolu:`, { id: user.id, role: user.role, nom: user.nom_complet });

    cacheSet(cacheKey, user);
    return user;
}

// ── authMiddleware ───────────────────────────────────────────
const authMiddleware = async (req, res, next) => {
    console.log('\n🔐 ===== AUTH =====');
    try {
        const authHeader = req.headers.authorization || '';
        const token = authHeader.replace('Bearer ', '').trim();

        if (!token) {
            return res.status(401).json({
                status: 'error', message: 'Token manquant', code: 'NO_TOKEN'
            });
        }

        const user = await resolveUser(token);

        if (!user) {
            return res.status(401).json({
                status: 'error', message: 'Token invalide ou expiré', code: 'INVALID_TOKEN'
            });
        }

        req.user = user;
        next();

    } catch (err) {
        console.error('❌ Auth middleware error:', err.message);
        res.status(500).json({
            status: 'error', message: 'Erreur authentification', code: 'AUTH_ERROR'
        });
    }
};

// ── checkRole ────────────────────────────────────────────────
// Usage: checkRole(['chef'])  ou  checkRole(['chef', 'admin'])
const checkRole = (allowedRoles) => (req, res, next) => {
    if (!req.user) {
        return res.status(401).json({
            status: 'error', message: 'Non authentifié', code: 'NOT_AUTHENTICATED'
        });
    }

    if (!allowedRoles.includes(req.user.role)) {
        console.log(`❌ Rôle "${req.user.role}" refusé — requis: [${allowedRoles.join(', ')}]`);
        return res.status(403).json({
            status:  'error',
            message: 'Accès refusé — privilèges insuffisants',
            code:    'INSUFFICIENT_PRIVILEGES',
            details: { required: allowedRoles, your_role: req.user.role }
        });
    }

    console.log(`✅ Rôle "${req.user.role}" autorisé`);
    next();
};

// ── Utilitaire : invalider cache après update rôle ───────────
const invalidateUser = (userId) => {
    _cache.delete(`user:${userId}`);
    console.log(`🗑️  Cache invalidé pour user ${userId}`);
};

module.exports = { authMiddleware, checkRole, invalidateUser };