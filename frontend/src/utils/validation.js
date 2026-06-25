/**
 * Frontend Input Validation Utilities
 * Validates data before sending to backend API
 */

/**
 * Validates IBGE code format (8 digits)
 * @param {string} codigoIBGE - The IBGE code to validate
 * @returns {{valid: boolean, error?: string}}
 */
export const validateIBGECode = (codigoIBGE) => {
  if (!codigoIBGE) {
    return { valid: false, error: 'Código IBGE é obrigatório' };
  }
  
  if (typeof codigoIBGE !== 'string' && typeof codigoIBGE !== 'number') {
    return { valid: false, error: 'Código IBGE deve ser texto ou número' };
  }
  
  const code = String(codigoIBGE).trim();
  
  if (!/^\d{8}$/.test(code)) {
    return { valid: false, error: 'Código IBGE deve ter exatamente 8 dígitos' };
  }
  
  return { valid: true };
};

/**
 * Validates city name
 * @param {string} nomeCidade - The city name to validate
 * @returns {{valid: boolean, error?: string}}
 */
export const validateCityName = (nomeCidade) => {
  if (!nomeCidade) {
    return { valid: false, error: 'Nome da cidade é obrigatório' };
  }
  
  if (typeof nomeCidade !== 'string') {
    return { valid: false, error: 'Nome da cidade deve ser texto' };
  }
  
  const name = nomeCidade.trim();
  
  if (name.length < 2) {
    return { valid: false, error: 'Nome da cidade deve ter pelo menos 2 caracteres' };
  }
  
  if (name.length > 100) {
    return { valid: false, error: 'Nome da cidade não pode ter mais de 100 caracteres' };
  }
  
  // Only allow letters, spaces, hyphens, and accented characters
  if (!/^[a-záàâãéèêíïóôõöúçñ\s\-]+$/i.test(name)) {
    return { valid: false, error: 'Nome da cidade contém caracteres inválidos' };
  }
  
  return { valid: true };
};

/**
 * Validates indicator value (0-100)
 * @param {number} value - The indicator value to validate
 * @param {string} indicatorName - The indicator name (for error messages)
 * @returns {{valid: boolean, error?: string}}
 */
export const validateIndicatorValue = (value, indicatorName = 'Indicador') => {
  if (value === null || value === undefined || value === '') {
    return { valid: false, error: `${indicatorName} é obrigatório` };
  }
  
  const numValue = Number(value);
  
  if (isNaN(numValue)) {
    return { valid: false, error: `${indicatorName} deve ser um número` };
  }
  
  if (numValue < 0) {
    return { valid: false, error: `${indicatorName} não pode ser negativo` };
  }
  
  if (numValue > 100) {
    return { valid: false, error: `${indicatorName} não pode ser maior que 100` };
  }
  
  return { valid: true };
};

/**
 * Validates a city input object
 * @param {Object} city - The city input object
 * @returns {{valid: boolean, errors: Object}}
 */
export const validateCityInput = (city) => {
  const errors = {};
  
  // Validate codigo_ibge
  const ibgeValidation = validateIBGECode(city.codigo_ibge);
  if (!ibgeValidation.valid) {
    errors.codigo_ibge = ibgeValidation.error;
  }
  
  // Validate nome_cidade
  const nameValidation = validateCityName(city.nome_cidade);
  if (!nameValidation.valid) {
    errors.nome_cidade = nameValidation.error;
  }
  
  // Validate manual_indicators if provided
  if (city.manual_indicators) {
    if (typeof city.manual_indicators !== 'object') {
      errors.manual_indicators = 'Indicadores manuais devem ser um objeto';
    }
  }
  
  return {
    valid: Object.keys(errors).length === 0,
    errors
  };
};

/**
 * Validates array of city inputs for TOPSIS ranking
 * @param {Array<Object>} cities - Array of city input objects
 * @returns {{valid: boolean, errors: Array}}
 */
export const validateRankingInput = (cities) => {
  const errors = [];
  
  if (!Array.isArray(cities)) {
    return {
      valid: false,
      errors: ['Entrada deve ser um array de cidades']
    };
  }
  
  if (cities.length < 2) {
    return {
      valid: false,
      errors: ['TOPSIS requer no mínimo 2 cidades para comparação']
    };
  }
  
  if (cities.length > 50) {
    return {
      valid: false,
      errors: ['Máximo 50 cidades por ranking']
    };
  }
  
  // Validate each city
  cities.forEach((city, index) => {
    const validation = validateCityInput(city);
    if (!validation.valid) {
      errors.push({
        index,
        city: city.nome_cidade || 'Desconhecida',
        errors: validation.errors
      });
    }
  });
  
  return {
    valid: errors.length === 0,
    errors
  };
};

/**
 * Validates API response data
 * @param {Object} response - The API response
 * @param {string} type - The expected response type (ranking, cities, indicators, snapshots)
 * @returns {{valid: boolean, error?: string}}
 */
export const validateAPIResponse = (response, type = 'ranking') => {
  if (!response) {
    return { valid: false, error: 'API retornou resposta vazia' };
  }
  
  switch (type) {
    case 'ranking':
      if (!Array.isArray(response.ranking)) {
        return { valid: false, error: 'Resposta de ranking deve conter array de rankings' };
      }
      if (response.ranking.length === 0) {
        return { valid: false, error: 'Nenhuma cidade no ranking' };
      }
      return { valid: true };
      
    case 'cities':
      if (!Array.isArray(response)) {
        return { valid: false, error: 'Resposta de cidades deve ser um array' };
      }
      return { valid: true };
      
    case 'indicators':
      if (!Array.isArray(response)) {
        return { valid: false, error: 'Resposta de indicadores deve ser um array' };
      }
      if (response.length !== 50) {
        return { valid: false, error: `Esperado 50 indicadores, recebido ${response.length}` };
      }
      return { valid: true };
      
    case 'snapshots':
      if (!Array.isArray(response)) {
        return { valid: false, error: 'Resposta de snapshots deve ser um array' };
      }
      return { valid: true };
      
    default:
      return { valid: true };
  }
};

export default {
  validateIBGECode,
  validateCityName,
  validateIndicatorValue,
  validateCityInput,
  validateRankingInput,
  validateAPIResponse
};
