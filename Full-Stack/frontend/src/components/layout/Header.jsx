import React from 'react';
import StatusBadge from '../common/StatusBadge';

export default function Header() {
  return (
    <header className="app-header">
      <div className="header-brand">
        <div className="brand-icon">DE</div>
        <div>
          <h1 className="brand-title">DubaiEstate AI 360</h1>
          <span className="brand-subtitle">Real Estate Intelligence Platform</span>
        </div>
      </div>
      <div className="header-meta">
        <StatusBadge type="info" label="Full Stack Domain" />
        <StatusBadge type="success" label="Week 1 — Day 1 Skeleton" />
      </div>
    </header>
  );
}
