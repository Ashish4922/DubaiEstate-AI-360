import React from 'react';
import './Common.css';

export default function StatusBadge({ label, type = 'info' }) {
  return (
    <span className={`status-badge status-badge-${type}`}>
      <span className="status-dot"></span>
      {label}
    </span>
  );
}
