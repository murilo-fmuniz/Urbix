import React, { useState } from 'react';
import './CityInputForm.css';
import { IBGE_MUNICIPALITIES, getMunicipalityOption } from '../data/ibgeCatalog';
const IBGE_COMMON_CITIES = IBGE_MUNICIPALITIES;

function CityInputForm({ onSubmit, loading }) {
  const [cities, setCities] = useState([
    { codigo_ibge: '', nome_cidade: '', manual_indicators: {} }
  ]);
  const [showManualForm, setShowManualForm] = useState({});

  const addCity = () => {
    setCities([...cities, { codigo_ibge: '', nome_cidade: '', manual_indicators: {} }]);
  };

  const removeCity = (index) => {
    if (cities.length > 1) {
      const newCities = cities.filter((_, i) => i !== index);
      setCities(newCities);
    }
  };

  const updateCityCode = (index, value) => {
    const newCities = [...cities];
    const cleanValue = value.replace(/\D/g, '').slice(0, 7); // Força apenas números
    newCities[index].codigo_ibge = cleanValue;
    
    // Extrair nome da cidade do dropdown
    const selectedCity = getMunicipalityOption(cleanValue);
    if (selectedCity) {
      const cityName = selectedCity.nome.split(' - ')[0];
      newCities[index].nome_cidade = cityName;
    } else if (cleanValue.length === 7) {
      // ✅ Fallback para a validação não bloquear IBGEs digitados manualmente
      newCities[index].nome_cidade = `Cidade IBGE ${cleanValue}`;
    } else {
      newCities[index].nome_cidade = '';
    }
    
    setCities(newCities);
  };

  const updateManualIndicator = (index, field, value) => {
    const newCities = [...cities];
    const manualIndicators = { ...newCities[index].manual_indicators };
    if (value === '') {
      delete manualIndicators[field];
    } else if (!Number.isNaN(Number(value))) {
      manualIndicators[field] = Number(value);
    }
    newCities[index].manual_indicators = manualIndicators;
    setCities(newCities);
  };

  const toggleManualForm = (index) => {
    setShowManualForm({
      ...showManualForm,
      [index]: !showManualForm[index],
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Validação: pelo menos uma cidade com código IBGE válido
    const validCities = cities.filter(c => c.codigo_ibge && c.codigo_ibge.trim().length > 0);
    if (validCities.length === 0) {
      alert('Por favor, insira pelo menos um código IBGE de cidade');
      return;
    }

    onSubmit(validCities);
  };

  return (
    <form className="city-input-form" onSubmit={handleSubmit}>
      <h2>📍 Selecione as Cidades</h2>

      <div className="cities-list">
        {cities.map((city, index) => (
          <div key={index} className="city-item">
            <div className="city-inputs">
              <div className="input-group">
                <label>Código IBGE ou Cidade</label>
                <select
                  value={city.codigo_ibge}
                  onChange={(e) => updateCityCode(index, e.target.value)}
                  className="city-select"
                >
                  <option value="">-- Selecionar cidade --</option>
                  {IBGE_COMMON_CITIES.map(c => (
                    <option key={c.codigo_ibge} value={c.codigo_ibge}>
                      {c.nome}
                    </option>
                  ))}
                </select>
                <small>Ou digite um código IBGE manualmente</small>
              </div>

              <input
                type="text"
                placeholder="Ex: 4101408 (se não selecionada acima)"
                value={city.codigo_ibge}
                onChange={(e) => updateCityCode(index, e.target.value)}
                className="manual-code-input"
                style={{ display: 'none' }}
              />
            </div>

            <div className="city-actions">
              <button
                type="button"
                className="btn-secondary"
                onClick={() => toggleManualForm(index)}
              >
                {showManualForm[index] ? '▼ Ocultar Manual' : '▶ Indicadores Manuais'}
              </button>

              {cities.length > 1 && (
                <button
                  type="button"
                  className="btn-danger"
                  onClick={() => removeCity(index)}
                >
                  Remover
                </button>
              )}
            </div>

            {/* FORM DE INDICADORES MANUAIS */}
            {showManualForm[index] && (
              <div className="manual-indicators-form">
                <h4>Indicadores Manuais (Prefeitura)</h4>
                <p className="form-hint">
                  Deixe em branco ou 0 para usar apenas dados das APIs
                </p>

                <div className="indicators-grid">
                  <div className="indicator-input">
                    <label>Estrutura municipal de TIC (0/1)</label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      placeholder="0"
                      onChange={(e) =>
                        updateManualIndicator(
                          index,
                          'estrutura_tic_municipal',
                          e.target.value
                        )
                      }
                    />
                  </div>

                  <div className="indicator-input">
                    <label>Atendimento de água SNIS (%)</label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      placeholder="0"
                      onChange={(e) =>
                        updateManualIndicator(
                          index,
                          'atendimento_agua_snis',
                          e.target.value
                        )
                      }
                    />
                  </div>

                  <div className="indicator-input">
                    <label>Bombeiros (numerador)</label>
                    <input
                      type="number"
                      min="0"
                      step="0.1"
                      placeholder="0"
                      onChange={(e) =>
                        updateManualIndicator(
                          index,
                          'bombeiros_numerador',
                          e.target.value
                        )
                      }
                    />
                  </div>

                  <div className="indicator-input">
                    <label>Atendimento de esgoto SNIS (%)</label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      placeholder="0"
                      onChange={(e) =>
                        updateManualIndicator(
                          index,
                          'atendimento_esgoto_snis',
                          e.target.value
                        )
                      }
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="form-actions">
        <button
          type="button"
          className="btn-secondary"
          onClick={addCity}
          disabled={loading}
        >
          + Adicionar Outra Cidade
        </button>

        <button
          type="submit"
          className="btn-primary"
          disabled={loading || cities.every(c => !c.codigo_ibge)}
        >
          {loading ? 'Processando...' : '🚀 Gerar Ranking'}
        </button>
      </div>
    </form>
  );
}

export default CityInputForm;
