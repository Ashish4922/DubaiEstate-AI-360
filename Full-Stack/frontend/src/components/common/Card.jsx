import React from 'react';
import './Common.css';

export default function Card({ title, subtitle, children, className = '' }) {
  return (
    <div className={`ui-card ${className}`}>
      {(title || subtitle) && (
        <div className="ui-card-header">
          {title && <h3 className="ui-card-title">{title}</h3>}
          {subtitle && <p className="ui-card-subtitle">{subtitle}</p>}
        </div>
      )}
      <div className="ui-card-body">{children}</div>
    </div>
  );
}
