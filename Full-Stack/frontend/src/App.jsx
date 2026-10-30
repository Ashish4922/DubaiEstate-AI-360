import React from 'react';
import MainLayout from './components/layout/MainLayout';
import Card from './components/common/Card';
import StatusBadge from './components/common/StatusBadge';
import { API_BASE_URL } from './services/api';
import './App.css';

export default function App() {
  return (
    <MainLayout>
      <div className="app-container">
        {/* Hero / Architecture Banner */}
        <section className="hero-section">
          <h2 className="hero-title">Full Stack Architecture Foundation</h2>
          <p className="hero-subtitle">
            DubaiEstate AI 360 is an agentic AI-powered real estate investment, brokerage,
            and property management intelligence platform. This frontend skeleton establishes
            the modular user interface architecture for Week 1.
          </p>
        </section>

        {/* System & Architecture Info Grid */}
        <div className="grid-two-column">
          <Card
            title="Frontend Architecture"
            subtitle="Client-side foundation built with React and Vite"
          >
            <ul className="info-list">
              <li className="info-item">
                <strong>Framework:</strong> React 18 (Vite 5 bundler)
              </li>
              <li className="info-item">
                <strong>Component Org:</strong> Reusable layout and UI elements
              </li>
              <li className="info-item">
                <strong>API Service:</strong> Centralized client (<code>src/services/api.js</code>)
              </li>
              <li className="info-item">
                <strong>API Endpoint:</strong> <code>{API_BASE_URL}</code>
              </li>
              <li className="info-item">
                <strong>Status:</strong>
                <StatusBadge type="success" label="Skeleton Ready" />
              </li>
            </ul>
          </Card>

          <Card
            title="Backend Architecture"
            subtitle="REST API foundation built with Python and FastAPI"
          >
            <ul className="info-list">
              <li className="info-item">
                <strong>Framework:</strong> FastAPI with Uvicorn ASGI
              </li>
              <li className="info-item">
                <strong>Structure:</strong> Modular routes, schemas, services, utils
              </li>
              <li className="info-item">
                <strong>Data Layer:</strong> Read-only access to shared CSV datasets
              </li>
              <li className="info-item">
                <strong>Security:</strong> Protected .env templates; no secrets committed
              </li>
              <li className="info-item">
                <strong>Status:</strong>
                <StatusBadge type="success" label="Skeleton Ready" />
              </li>
            </ul>
          </Card>
        </div>

        {/* Milestone Roadmap */}
        <Card
          title="Week 1 Development Roadmap"
          subtitle="Full Stack implementation milestones according to the task plan"
        >
          <ul className="roadmap-list">
            <li className="roadmap-item">
              <span className="roadmap-title">Day 1: Architecture, Frontend/Backend Skeletons &amp; Environment Setup</span>
              <StatusBadge type="success" label="Completed" />
            </li>
            <li className="roadmap-item">
              <span className="roadmap-title">Day 2: Health Check API Endpoint &amp; Verification Tests</span>
              <StatusBadge type="info" label="Planned (Next)" />
            </li>
            <li className="roadmap-item">
              <span className="roadmap-title">Day 3: Read-Only Transactions Ingestion &amp; API Routes</span>
              <StatusBadge type="warning" label="Upcoming" />
            </li>
            <li className="roadmap-item">
              <span className="roadmap-title">Day 4: Data Filtering, Pagination &amp; Query Parameters</span>
              <StatusBadge type="warning" label="Upcoming" />
            </li>
            <li className="roadmap-item">
              <span className="roadmap-title">Day 5: Transactions Table UI &amp; Full Stack Integration</span>
              <StatusBadge type="warning" label="Upcoming" />
            </li>
          </ul>
        </Card>
      </div>
    </MainLayout>
  );
}
