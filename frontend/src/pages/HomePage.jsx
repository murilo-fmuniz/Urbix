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
          <Link to="/dashboard" className="button-primary">
            Ver Dashboard
          </Link>
        </div>
      </section>
      
      <section className="features container">
        <h2>Principais Recursos</h2>
        <div className="features-grid">
          <div className="feature-card card">
            <h3>Análise de Indicadores</h3>
            <p>
              Visualize e analise indicadores chave de desempenho para cidades
              inteligentes.
            </p>
          </div>
          <div className="feature-card card">
            <h3>Baseado em ISO 37100</h3>
            <p>
              Metodologia alinhada com padrões internacionais para cidades
              sustentáveis.
            </p>
          </div>
          <div className="feature-card card">
            <h3>Visualização Intuitiva</h3>
            <p>
              Interface clara e objetiva para facilitar a compreensão dos dados.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

export default HomePage;