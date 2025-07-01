// Configuración de API
const API_CONFIG = {
    BASE_URL: 'https://scoutgine-backend.onrender.com',
    // Para desarrollo local descomenta esta línea:
    // BASE_URL: 'http://localhost:8000'
};

// Función helper
function getApiUrl(endpoint) {
    return API_CONFIG.BASE_URL + endpoint;
}

// Exportar para uso global
window.API_CONFIG = API_CONFIG;
window.getApiUrl = getApiUrl;