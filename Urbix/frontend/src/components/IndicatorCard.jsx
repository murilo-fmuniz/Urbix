import React from 'react';
import './IndicatorCard.css';

function IndicatorCard({ indicator }) {
  const progress = (indicator.value / indicator.target) * 100;
  
  return (
    <div className="indicator-card card">
      <h3>{indicator.name}</h3>
      <p className="category">{indicator.category}</p>
      <div className="progress-container">
        <div 
          className="progress-bar" 
          style={{ width: `${Math.min(progress, 100)}%` }}
        />
      </div>
      <div className="values">
        <span>Atual: {indicator.value}%</span>
        <span>Meta: {indicator.target}%</span>
      </div>
      <p className="description">{indicator.description}</p>
    </div>
  );
}

export default IndicatorCard;