import React, { useState, useEffect } from 'react';
import '../styles/demo-ideas-catalog.css';

const i18n = {
  es: {
    toggleOpen: 'Mostrar sandbox de ideas demo (deteccion de duplicidad)',
    toggleClose: 'Ocultar sandbox de ideas demo',
    title: 'Sandbox de Ideas Demo',
    subtitle: 'Ideas de ejemplo precargadas para demostrar la deteccion de duplicidad por contexto',
    hint:
      'Usa estos casos para demostrar como la plataforma detecta ideas similares: registra una nueva idea con un titulo o problema parecido a uno de estos ejemplos y el sistema mostrara una alerta indicando que ya existe una iniciativa en curso, junto con el contacto del responsable.',
    loadingIdeas: 'Cargando ideas demo...',
    errorLoading: 'Error al cargar ideas demo',
    noIdeas: 'No hay ideas demo cargadas en este momento',
    loadSamples: 'Cargar ideas de ejemplo',
    loadingSamples: 'Cargando ejemplos...',
    reload: 'Recargar ejemplos',
    owner: 'Responsable',
    language: 'Idioma',
    problem: 'Problema',
    expectedValue: 'Valor Esperado',
    affectedUsers: 'Usuarios Afectados',
    valueScore: 'Score Valor',
    riskScore: 'Score Riesgo',
    deleteConfirm: '¿Eliminar esta idea de demostración? Podrás volver a cargarla luego.',
    deleteButton: 'Eliminar',
    deleteSuccess: 'Idea eliminada correctamente',
    deleteError: 'Error al eliminar idea',
    seedError: 'Error al cargar ideas de ejemplo',
    useInForm: 'Usar en el formulario',
    usedInForm: 'Cargado en el formulario de arriba',
  },
  en: {
    toggleOpen: 'Show demo ideas sandbox (duplicate detection)',
    toggleClose: 'Hide demo ideas sandbox',
    title: 'Demo Ideas Sandbox',
    subtitle: 'Preloaded example ideas to demonstrate context-based duplicate detection',
    hint:
      'Use these cases to demonstrate how the platform detects similar ideas: submit a new idea with a title or problem similar to one of these examples and the system will show a warning that a similar initiative is already in progress, along with the owner contact.',
    loadingIdeas: 'Loading demo ideas...',
    errorLoading: 'Error loading demo ideas',
    noIdeas: 'No demo ideas loaded right now',
    loadSamples: 'Load sample ideas',
    loadingSamples: 'Loading samples...',
    reload: 'Reload samples',
    owner: 'Owner',
    language: 'Language',
    problem: 'Problem',
    expectedValue: 'Expected Value',
    affectedUsers: 'Affected Users',
    valueScore: 'Value Score',
    riskScore: 'Risk Score',
    deleteConfirm: 'Delete this demonstration idea? You can reload it later.',
    deleteButton: 'Delete',
    deleteSuccess: 'Idea deleted successfully',
    deleteError: 'Error deleting idea',
    seedError: 'Error loading sample ideas',
    useInForm: 'Use in form',
    usedInForm: 'Loaded into the form above',
  },
  pt: {
    toggleOpen: 'Mostrar sandbox de ideias demo (deteccao de duplicidade)',
    toggleClose: 'Ocultar sandbox de ideias demo',
    title: 'Sandbox de Ideias Demo',
    subtitle: 'Ideias de exemplo pre-carregadas para demonstrar a deteccao de duplicidade por contexto',
    hint:
      'Use estes casos para demonstrar como a plataforma detecta ideias similares: registre uma nova ideia com titulo ou problema parecido a um destes exemplos e o sistema mostrara um alerta indicando que ja existe uma iniciativa em andamento, junto com o contato do responsavel.',
    loadingIdeas: 'Carregando ideias demo...',
    errorLoading: 'Erro ao carregar ideias demo',
    noIdeas: 'Nenhuma ideia demo carregada no momento',
    loadSamples: 'Carregar ideias de exemplo',
    loadingSamples: 'Carregando exemplos...',
    reload: 'Recarregar exemplos',
    owner: 'Responsavel',
    language: 'Idioma',
    problem: 'Problema',
    expectedValue: 'Valor Esperado',
    affectedUsers: 'Usuarios Afetados',
    valueScore: 'Score Valor',
    riskScore: 'Score Risco',
    deleteConfirm: 'Excluir esta ideia de demonstração? Você pode recarregá-la depois.',
    deleteButton: 'Excluir',
    deleteSuccess: 'Ideia excluída com sucesso',
    deleteError: 'Erro ao excluir ideia',
    seedError: 'Erro ao carregar ideias de exemplo',
    useInForm: 'Usar no formulário',
    usedInForm: 'Carregado no formulário acima',
  },
};

export default function DemoIdeasCatalog({ lang = 'es', apiUrl, authToken, onUseExample }) {
  const [expanded, setExpanded] = useState(false);
  const [ideas, setIdeas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [error, setError] = useState(null);
  const [selectedIdeaId, setSelectedIdeaId] = useState(null);
  const [deleting, setDeleting] = useState({});
  const [loaded, setLoaded] = useState(false);
  const [usedIdeaId, setUsedIdeaId] = useState(null);

  const t = i18n[lang] || i18n.es;

  useEffect(() => {
    if (expanded && !loaded) {
      loadDemoSamples();
    }
  }, [expanded]);

  function authHeaders() {
    return authToken ? { Authorization: `Bearer ${authToken}` } : {};
  }

  async function loadDemoSamples() {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${apiUrl}/ideas/demo-samples`, {
        headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        throw new Error(t.errorLoading);
      }
      const data = await response.json();
      setIdeas(data);
      setLoaded(true);
    } catch (err) {
      setError(err.message || t.errorLoading);
      console.error('Error loading demo samples:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSeedSamples() {
    try {
      setSeeding(true);
      setError(null);
      const response = await fetch(`${apiUrl}/ideas/demo-samples/seed`, {
        method: 'POST',
        headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        throw new Error(t.seedError);
      }
      const data = await response.json();
      setIdeas(data);
      setLoaded(true);
    } catch (err) {
      setError(err.message || t.seedError);
      console.error('Error seeding demo samples:', err);
    } finally {
      setSeeding(false);
    }
  }

  async function handleDeleteIdea(ideaId) {
    if (!window.confirm(t.deleteConfirm)) return;

    try {
      setDeleting((prev) => ({ ...prev, [ideaId]: true }));
      const response = await fetch(`${apiUrl}/ideas/demo-samples/${ideaId}`, {
        method: 'DELETE',
        headers: { ...authHeaders(), 'Content-Type': 'application/json' },
      });
      if (!response.ok) {
        throw new Error(t.deleteError);
      }
      setIdeas((prev) => prev.filter((idea) => idea.idea_id !== ideaId));
    } catch (err) {
      alert(err.message || t.deleteError);
      console.error('Error deleting demo sample:', err);
    } finally {
      setDeleting((prev) => ({ ...prev, [ideaId]: false }));
    }
  }

  return (
    <section className="demo-ideas-catalog card card-list">
      <button
        type="button"
        className="demo-toggle-btn"
        onClick={() => setExpanded((prev) => !prev)}
      >
        {expanded ? t.toggleClose : t.toggleOpen}
      </button>

      {expanded && (
        <div className="demo-sandbox-body">
          <div className="card-header">
            <h2>{t.title}</h2>
            <p>{t.subtitle}</p>
          </div>
          <p className="meta demo-hint">{t.hint}</p>

          <div className="action-row" style={{ margin: '10px 0' }}>
            <button type="button" onClick={handleSeedSamples} disabled={seeding}>
              {seeding ? t.loadingSamples : ideas.length > 0 ? t.reload : t.loadSamples}
            </button>
          </div>

          {loading && <p className="meta">{t.loadingIdeas}</p>}
          {error && <p className="meta" style={{ color: '#d97706' }}>{error}</p>}
          {!loading && !error && ideas.length === 0 && <p className="meta">{t.noIdeas}</p>}

          {ideas.length > 0 && (
            <div className="ideas-grid">
              {ideas.map((idea) => (
                <div
                  key={idea.idea_id}
                  className={`idea-card ${idea.status}`}
                  onClick={() => setSelectedIdeaId(selectedIdeaId === idea.idea_id ? null : idea.idea_id)}
                >
                  <div className="idea-header">
                    <h3>{idea.title}</h3>
                  </div>
                  <p className="meta">{t.owner}: {idea.owner_display_name}</p>
                  <p className="meta">{t.language}: <strong>{idea.source_language?.toUpperCase() || 'es'}</strong></p>

                  {selectedIdeaId === idea.idea_id && (
                    <div className="idea-details">
                      <p className="meta"><strong>{t.problem}:</strong> {idea.problem_statement}</p>
                      <p className="meta"><strong>{t.expectedValue}:</strong> {idea.expected_value}</p>
                      {idea.affected_users?.length > 0 && (
                        <p className="meta">
                          <strong>{t.affectedUsers}:</strong> {idea.affected_users.join(', ')}
                        </p>
                      )}
                      {idea.business_validation && (
                        <div className="scores">
                          <span className="score">{t.valueScore}: {idea.business_validation.value_score}</span>
                          <span className="score">{t.riskScore}: {idea.business_validation.risk_score}</span>
                        </div>
                      )}
                      <div className="action-row" style={{ marginTop: 10 }}>
                        <button
                          type="button"
                          className="btn-use-example"
                          onClick={(e) => {
                            e.stopPropagation();
                            if (onUseExample) {
                              onUseExample(idea);
                              setUsedIdeaId(idea.idea_id);
                            }
                          }}
                        >
                          {t.useInForm}
                        </button>
                        <button
                          type="button"
                          className="btn-delete"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleDeleteIdea(idea.idea_id);
                          }}
                          disabled={deleting[idea.idea_id]}
                        >
                          {deleting[idea.idea_id] ? '...' : t.deleteButton}
                        </button>
                      </div>
                      {usedIdeaId === idea.idea_id && (
                        <p className="meta used-in-form-hint">{t.usedInForm}</p>
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
