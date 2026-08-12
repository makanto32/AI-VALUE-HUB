import React, { useState, useEffect } from 'react';
import '../styles/production-ideas-catalog.css';

const i18n = {
  es: {
    toggleOpen: 'Mostrar catálogo de ideas en producción',
    toggleClose: 'Ocultar catálogo de ideas en producción',
    title: 'Catálogo de Ideas en Producción',
    subtitle: 'Casos de uso ya desplegados en producción dentro de tu organización',
    loading: 'Cargando ideas en producción...',
    error: 'Error al cargar ideas en producción',
    empty: 'Todavía no hay ideas desplegadas en producción para este tenant',
    owner: 'Responsable',
    problem: 'Problema',
    expectedValue: 'Valor esperado',
    valueScore: 'Score Valor',
    riskScore: 'Score Riesgo',
  },
  en: {
    toggleOpen: 'Show production ideas catalog',
    toggleClose: 'Hide production ideas catalog',
    title: 'Production Ideas Catalog',
    subtitle: 'Use cases already deployed to production within your organization',
    loading: 'Loading production ideas...',
    error: 'Error loading production ideas',
    empty: 'No ideas deployed to production yet for this tenant',
    owner: 'Owner',
    problem: 'Problem',
    expectedValue: 'Expected value',
    valueScore: 'Value Score',
    riskScore: 'Risk Score',
  },
  pt: {
    toggleOpen: 'Mostrar catálogo de ideias em produção',
    toggleClose: 'Ocultar catálogo de ideias em produção',
    title: 'Catálogo de Ideias em Produção',
    subtitle: 'Casos de uso já implantados em produção dentro da sua organização',
    loading: 'Carregando ideias em produção...',
    error: 'Erro ao carregar ideias em produção',
    empty: 'Ainda não há ideias implantadas em produção para este tenant',
    owner: 'Responsável',
    problem: 'Problema',
    expectedValue: 'Valor esperado',
    valueScore: 'Score Valor',
    riskScore: 'Score Risco',
  },
};

export default function ProductionIdeasCatalog({ lang = 'es', apiUrl, authToken }) {
  const [expanded, setExpanded] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [ideas, setIdeas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedId, setExpandedId] = useState(null);

  const t = i18n[lang] || i18n.es;

  useEffect(() => {
    if (expanded && !loaded) {
      loadProductionIdeas();
    }
  }, [expanded]);

  async function loadProductionIdeas() {
    try {
      setLoading(true);
      setError(null);
      const headers = authToken ? { Authorization: `Bearer ${authToken}` } : {};

      const response = await fetch(`${apiUrl}/ideas?deployment_status=production`, {
        headers: { ...headers, 'Content-Type': 'application/json' },
      });

      if (!response.ok) {
        throw new Error(t.error);
      }

      const data = await response.json();
      setIdeas(data);
      setLoaded(true);
    } catch (err) {
      setError(err.message || t.error);
      console.error('Error loading production ideas:', err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="production-ideas-catalog card card-list">
      <button
        type="button"
        className="production-toggle-btn"
        onClick={() => setExpanded((prev) => !prev)}
      >
        {expanded ? t.toggleClose : t.toggleOpen}
      </button>

      {expanded && (
        <div className="production-catalog-body">
          <div className="card-header">
            <h2>{t.title}</h2>
            <p>{t.subtitle}</p>
          </div>

          {loading && <p className="meta">{t.loading}</p>}
          {error && <p className="meta" style={{ color: '#d97706' }}>{error}</p>}
          {!loading && !error && ideas.length === 0 && <p className="meta">{t.empty}</p>}

          {ideas.length > 0 && (
            <div className="production-ideas-grid">
              {ideas.map((idea) => (
                <div
                  key={idea.idea_id}
                  className="production-idea-card"
                  onClick={() => setExpandedId(expandedId === idea.idea_id ? null : idea.idea_id)}
                >
                  <div className="production-idea-header">
                    <h3>{idea.title}</h3>
                    <span className="production-badge">production</span>
                  </div>
                  <p className="meta">{t.owner}: {idea.owner_display_name}</p>

                  {expandedId === idea.idea_id && (
                    <div className="production-idea-details">
                      <p className="meta"><strong>{t.problem}:</strong> {idea.problem_statement}</p>
                      <p className="meta"><strong>{t.expectedValue}:</strong> {idea.expected_value}</p>
                      {idea.business_validation && (
                        <div className="scores">
                          <span className="score">{t.valueScore}: {idea.business_validation.value_score}</span>
                          <span className="score">{t.riskScore}: {idea.business_validation.risk_score}</span>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}
