import React, { useMemo, useState } from 'react';
import ManualDataForm from '../components/ManualDataForm';
import './AdminCidadesPage.css';

const CITY_PRESETS = [
  { codigo_ibge: '9999999', nome_cidade: 'UTFPRCity - PR' },
  { codigo_ibge: '4101408', nome_cidade: 'Apucarana - PR' },
  { codigo_ibge: '4113700', nome_cidade: 'Londrina - PR' },
  { codigo_ibge: '3304557', nome_cidade: 'Rio de Janeiro - RJ' },
  { codigo_ibge: '3550308', nome_cidade: 'São Paulo - SP' },
];

const MANUAL_ONLY_FIELDS = [
  'Bombeiros (100k hab)',
  'Mortes por Incêndio (100k hab)',
  'Agentes de Polícia (100k hab)',
  'Sobrevivência Novos Negócios (100k hab)',
  'Empregos em TIC (% força de trabalho)',
  'Graduados STEM (100k hab)',
  'Energia de Resíduos (% energia total)',
  'Iluminação Pública com Telegestão (%)',
  'Edifícios Verdes Certificados (%)',
  'Monitoramento Ar em Tempo Real (%)',
  'Serviços Urbanos Online (%)',
  'Prontuário Eletrônico (% população)',
  'Consultas Remotas (100k hab)',
  'Medidores Inteligentes Água (%)',
  'Áreas Cobertas por Câmeras (% cidade)',
  'Lixeiras com Sensores (%)',
  'Semáforos Inteligentes (%)',
  'Seguro contra Ameaças (% população)',
  'Empregos Informais (% força de trabalho)',
  'Escolas com Plano Emergência (%)',
  'População Treinada em Emergência (%)',
  'Hospitais com Gerador Backup (%)',
  'Seguro Saúde Básico (% população)',
  'Imunização (%)',
  'Abrigos de Emergência (100k hab)',
  'Edifícios Vulneráveis a Desastres (%)',
  'Rotas de Evacuação Identificadas (100k)',
  'Reservas de Alimentos 72h (%)',
  'Mapas de Ameaças Públicos (%)',
  'Pessoas Afetadas por Desastres (100k hab)',
  'Danos à Infraestrutura Básica (%)',
];

function AdminCidadesPage() {
  const [presetIndex, setPresetIndex] = useState(0);
  const [helpOpen, setHelpOpen] = useState(false);

  const selectedPreset = useMemo(() => CITY_PRESETS[presetIndex], [presetIndex]);

  return (
    <div className="admin-cidades-page">
      <section className="admin-hero card">
        <p className="eyebrow">Administração / Dados Manuais</p>
        <h1>CRUD de dados específicos por cidade</h1>
        <p className="hero-copy">
          Esta área serve para criar, consultar, atualizar e excluir os dados manuais das cidades.
          O visual segue a mesma linguagem do Urbix: fundo claro, cards brancos e destaque em laranja.
        </p>

        <div className="admin-hero-actions">
          <span className="pill pill-primary">Apucarana como teste</span>
          <span className="pill">Banco integrado</span>
          <span className="pill">CRUD completo</span>
          <button
            type="button"
            className="pill pill-help"
            onClick={() => setHelpOpen(true)}
          >
            ❔ Ajuda / Saiba mais
          </button>
        </div>
      </section>

      {helpOpen && (
        <div className="help-modal-backdrop" onClick={() => setHelpOpen(false)}>
          <div className="help-modal card" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="help-modal-title">
            <div className="help-modal-header">
              <div>
                <p className="eyebrow">Ajuda</p>
                <h2 id="help-modal-title">Como usar esta página</h2>
              </div>
              <button type="button" className="help-close-button" onClick={() => setHelpOpen(false)} aria-label="Fechar ajuda">
                ✕
              </button>
            </div>

            <p className="help-modal-copy">
              Esta área foi feita para manter os dados específicos da cidade integrados ao backend.
              Você pode selecionar uma cidade de teste, preencher valores manuais e salvar no banco.
            </p>

            <div className="help-modal-grid">
              <div className="help-box">
                <h3>O que pode ser preenchido manualmente?</h3>
                <p>
                  Indicadores que ainda não vêm diretamente por API, como itens de segurança,
                  mobilidade, resiliência e infraestrutura urbana específica.
                </p>
              </div>
              <div className="help-box">
                <h3>Como testar?</h3>
                <p>
                  Use <strong>UTFPRCity (9999999)</strong> como cidade inicial. Depois ajuste os campos,
                  salve e confira se o histórico e a exclusão funcionam corretamente.
                </p>
              </div>
            </div>

            <div className="help-fields-section">
              <h3>Campos sem API direta</h3>
              <p>
                Esses itens estão ocultos da tela principal para não poluir o preenchimento. Eles ficam
                aqui como referência rápida quando precisar revisar o que ainda depende de inserção manual.
              </p>

              <div className="field-tags help-field-tags">
                {MANUAL_ONLY_FIELDS.map((field) => (
                  <span key={field} className="field-tag">
                    {field}
                  </span>
                ))}
              </div>
            </div>

            <div className="help-modal-footer">
              <button type="button" className="help-action-button" onClick={() => setHelpOpen(false)}>
                Entendi
              </button>
            </div>
          </div>
        </div>
      )}

      <section className="admin-grid">
        <aside className="card admin-card sidebar-card">
          <div className="card-header">
            <h2>Cidade de teste</h2>
            <p>Escolha uma cidade para iniciar o preenchimento manual com valores de exemplo.</p>
          </div>

          <div className="preset-list">
            {CITY_PRESETS.map((city, index) => (
              <button
                key={city.codigo_ibge}
                type="button"
                onClick={() => setPresetIndex(index)}
                className={`preset-item ${index === presetIndex ? 'active' : ''}`}
              >
                <strong>{city.nome_cidade}</strong>
                <span>IBGE {city.codigo_ibge}</span>
              </button>
            ))}
          </div>

          <div className="current-preset">
            <span className="current-label">Preset ativo</span>
            <strong>{selectedPreset.nome_cidade}</strong>
            <small>IBGE {selectedPreset.codigo_ibge}</small>
          </div>
        </aside>
      </section>

      <section className="card admin-form-card">
        <div className="card-header">
          <h2>Formulário de dados manuais</h2>
          <p>Use o formulário abaixo para editar os indicadores da cidade selecionada.</p>
        </div>
        <ManualDataForm key={selectedPreset.codigo_ibge} defaultCityPreset={selectedPreset} />
      </section>
    </div>
  );
}

export default AdminCidadesPage;