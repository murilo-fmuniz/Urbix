import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

function HomePage() {
  return (
    <div className="home-page">
      <section className="hero">
        <div className="container">
          <h1>Urbix</h1>
          <p>
            Análise e visualização de indicadores de maturidade para Cidades
            Sustentáveis, baseado na Norma ISO 37100
          </p>
          <div className="cta-buttons">
            <Link to="/ranking" className="button-primary">
              Gerar Ranking TOPSIS
            </Link>
          </div>
        </div>
      </section>
      
      <section className="features container">
        <h2>Principais Recursos</h2>
        <div className="features-grid">
          <div className="feature-card card">
            <h3>🏆 Ranking TOPSIS</h3>
            <p>
              Gere rankings de cidades inteligentes usando dados das APIs governamentais
              (IBGE, SICONFI, DataSUS) combinados com indicadores manuais.
            </p>
          </div>
          <div className="feature-card card">
            <h3>📊 Dashboard Analítico</h3>
            <p>
              Visualize e analise indicadores chave de desempenho para cidades
              inteligentes com filtros avançados.
            </p>
          </div>
          <div className="feature-card card">
            <h3>✅ Baseado em ISO 37100</h3>
            <p>
              Metodologia alinhada com padrões internacionais para cidades
              sustentáveis e inteligentes.
            </p>
          </div>
          <div className="feature-card card">
            <h3>🔗 Dados Híbridos</h3>
            <p>
              Integração automática de dados de APIs governamentais com indicadores
              manuais fornecidos pelas prefeituras.
            </p>
          </div>
          <div className="feature-card card">
            <h3>📈 Visualização Intuitiva</h3>
            <p>
              Interface clara e objetiva com gráficos, tabelas e comparações para
              facilitar a compreensão dos dados.
            </p>
          </div>
          <div className="feature-card card">
            <h3>⚙️ Cálculo TOPSIS</h3>
            <p>
              Método multicritério TOPSIS para análise de similaridade com ideais
              positivo e negativo.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default HomePage;