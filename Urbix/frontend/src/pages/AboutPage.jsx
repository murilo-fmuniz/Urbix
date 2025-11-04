import React from 'react';
import './AboutPage.css';

function AboutPage() {
  return (
    <div className="about-page container">
      <h1>Sobre o Projeto</h1>
      <section className="about-content">
        <h2>O que é o Urbix?</h2>
        <p>
          O Urbix é uma ferramenta de análise e visualização de indicadores de
          maturidade para Cidades Sustentáveis, desenvolvida com base na Norma ISO
          37100. Este projeto faz parte de uma Iniciação Científica que busca
          contribuir para o desenvolvimento de cidades mais inteligentes e
          sustentáveis.
        </p>

        <h2>Norma ISO 37100</h2>
        <p>
          A ISO 37100 fornece uma terminologia padronizada para o desenvolvimento
          sustentável em comunidades urbanas. Esta norma estabelece definições e
          conceitos fundamentais relacionados ao desenvolvimento sustentável em
          comunidades, incluindo cidades inteligentes e resilientes.
        </p>

        <h2>Objetivos</h2>
        <ul>
          <li>Monitorar indicadores de sustentabilidade urbana</li>
          <li>Facilitar a tomada de decisões baseada em dados</li>
          <li>Promover transparência na gestão urbana</li>
          <li>Contribuir para o desenvolvimento de cidades mais inteligentes</li>
        </ul>
      </section>
    </div>
  );
}

export default AboutPage;