import React, { useState } from 'react';
import './CityInputForm.css';

const IBGE_COMMON_CITIES = [
  { codigo: '4101408', nome: 'Apucarana - PR' },
  { codigo: '4113700', nome: 'Londrina - PR' },
  { codigo: '4115200', nome: 'Maringá - PR' },
  { codigo: '3550308', nome: 'São Paulo - SP' },
  { codigo: '3106200', nome: 'Belo Horizonte - MG' },
  { codigo: '1300260', nome: 'Brasília - DF' },
  { codigo: '3304557', nome: 'Rio de Janeiro - RJ' },
  { codigo: '4203402', nome: 'Florianópolis - SC' },
];

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
    newCities[index].codigo_ibge = value;
    // Extrair nome da cidade do dropdown (formato: 'Londrina - PR')
    const selectedCity = IBGE_COMMON_CITIES.find(c => c.codigo === value);
    if (selectedCity) {
      const cityName = selectedCity.nome.split(' - ')[0]; // Pega apenas 'Londrina'
      newCities[index].nome_cidade = cityName;
    }
    setCities(newCities);
  };

  const updateManualIndicator = (index, field, value) => {
    const newCities = [...cities];
    newCities[index].manual_indicators = {
      ...newCities[index].manual_indicators,
      [field]: value ? parseFloat(value) : 0.0,
    };
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
                    <option key={c.codigo} value={c.codigo}>
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
                    <label>Iluminação com Telegestão (%)</label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      placeholder="0"
                      onChange={(e) =>
                        updateManualIndicator(
                          index,
                          'pontos_iluminacao_telegestao',
                          e.target.value
                        )
                      }
                    />
                  </div>

                  <div className="indicator-input">
                    <label>Medidores Inteligentes Energia (%)</label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      placeholder="0"
                      onChange={(e) =>
                        updateManualIndicator(
                          index,
                          'medidores_inteligentes_energia',
                          e.target.value
                        )
                      }
                    />
                  </div>

                  <div className="indicator-input">
                    <label>Bombeiros por 100k hab</label>
                    <input
                      type="number"
                      min="0"
                      step="0.1"
                      placeholder="0"
                      onChange={(e) =>
                        updateManualIndicator(
                          index,
                          'bombeiros_por_100k',
                          e.target.value
                        )
                      }
                    />
                  </div>

                  <div className="indicator-input">
                    <label>Área Verde Mapeada (%)</label>
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      placeholder="0"
                      onChange={(e) =>
                        updateManualIndicator(
                          index,
                          'area_verde_mapeada',
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
