import React, { useEffect, useState } from 'react';
import styles from '../styles/dashboard.module.css';

const API_URL = import.meta.env.VITE_API_URL || "https://aihub-api-dev.yellowwave-f693504a.eastus.azurecontainerapps.io";

const i18n: Record<string, Record<string, string>> = {
  es: {
    title: 'Tablero - Métricas de Valor IA',
    periodCurrent: 'Período Actual',
    periodLastQuarter: 'Último Trimestre',
    periodLastYear: 'Último Año',
    kpiRework: 'Reducción de Retrabajo',
    kpiReworkDesc: 'vs. proceso manual',
    kpiDuplicates: 'Duplicados Evitados',
    kpiDuplicatesDesc: 'de ideas analizadas',
    kpiCollaboration: 'Participación de Colaboradores',
    kpiCollaborationDesc: 'tasa de adopción',
    kpiAiAdoption: 'Adopción de IA',
    kpiAiAdoptionDesc: 'ideas validadas por IA',
    sectionDuplication: 'Métricas de Duplicación y Control',
    totalIdeas: 'Total de Ideas',
    duplicatesDetected: 'Duplicados Detectados',
    costAvoided: 'Costo Evitado USD',
    avgSimilarity: 'Similitud Promedio',
    sectionAdoption: 'Adopción y Utilización de IA',
    ideasValidatedAI: 'Ideas Validadas con IA',
    of: 'de',
    agentAssisted: 'Validaciones Asistidas por Agente',
    avgQuestionsPerIdea: 'Promedio Preguntas por Idea',
    validationPatterns: 'Patrones de Validación',
    sectionProduction: 'Impacto en Producción',
    ideasInProd: 'Ideas en Producción',
    annualValue: 'Valor Anual Estimado',
    hoursSaved: 'Horas Ahorradas Anualmente',
    successRate: 'Tasa de Éxito',
    topByValue: 'Top Ideas por Valor',
    sectionROI: 'ROI e Inversión en IA',
    annualInvestment: 'Inversión Anual',
    annualValueGenerated: 'Valor Generado Anualmente',
    roi: 'ROI %',
    payback: 'Payback Period',
    months: 'meses',
    sectionCollaborators: 'Top Colaboradores',
    colName: 'Nombre',
    colIdeasSubmitted: 'Ideas Enviadas',
    colApproved: 'Aprobadas',
    colParticipation: 'Participación %',
    colLastContrib: 'Última Contribución',
    sectionTrends: 'Tendencias Mensuales',
    trendSubmitted: 'Ideas Enviadas por Mes',
    trendApproved: 'Ideas Aprobadas por Mes',
    trendCost: 'Costo Mensual IA',
    trendTotal: 'Total',
    trendAvg: 'Promedio',
    trendAnnual: 'Total anual',
    footerMsg: 'Dashboard actualizado en tiempo real. Última actualización',
    loading: 'Cargando métricas ejecutivas...',
  },
  en: {
    title: 'Dashboard - AI Value Metrics',
    periodCurrent: 'Current Period',
    periodLastQuarter: 'Last Quarter',
    periodLastYear: 'Last Year',
    kpiRework: 'Rework Reduction',
    kpiReworkDesc: 'vs. manual process',
    kpiDuplicates: 'Duplicates Avoided',
    kpiDuplicatesDesc: 'of analyzed ideas',
    kpiCollaboration: 'Collaborator Participation',
    kpiCollaborationDesc: 'adoption rate',
    kpiAiAdoption: 'AI Adoption',
    kpiAiAdoptionDesc: 'ideas validated by AI',
    sectionDuplication: 'Duplication & Control Metrics',
    totalIdeas: 'Total Ideas',
    duplicatesDetected: 'Duplicates Detected',
    costAvoided: 'Avoided Cost (USD)',
    avgSimilarity: 'Avg. Similarity',
    sectionAdoption: 'AI Adoption & Utilization',
    ideasValidatedAI: 'Ideas Validated with AI',
    of: 'of',
    agentAssisted: 'Agent-Assisted Validations',
    avgQuestionsPerIdea: 'Avg. Questions per Idea',
    validationPatterns: 'Validation Patterns',
    sectionProduction: 'Production Impact',
    ideasInProd: 'Ideas in Production',
    annualValue: 'Estimated Annual Value',
    hoursSaved: 'Hours Saved Annually',
    successRate: 'Success Rate',
    topByValue: 'Top Ideas by Value',
    sectionROI: 'ROI & AI Investment',
    annualInvestment: 'Annual Investment',
    annualValueGenerated: 'Annual Value Generated',
    roi: 'ROI %',
    payback: 'Payback Period',
    months: 'months',
    sectionCollaborators: 'Top Collaborators',
    colName: 'Name',
    colIdeasSubmitted: 'Ideas Submitted',
    colApproved: 'Approved',
    colParticipation: 'Participation %',
    colLastContrib: 'Last Contribution',
    sectionTrends: 'Monthly Trends',
    trendSubmitted: 'Ideas Submitted per Month',
    trendApproved: 'Ideas Approved per Month',
    trendCost: 'Monthly AI Cost',
    trendTotal: 'Total',
    trendAvg: 'Average',
    trendAnnual: 'Annual total',
    footerMsg: 'Dashboard updated in real time. Last update',
    loading: 'Loading executive metrics...',
  },
  pt: {
    title: 'Painel - Métricas de Valor da IA',
    periodCurrent: 'Período Atual',
    periodLastQuarter: 'Último Trimestre',
    periodLastYear: 'Último Ano',
    kpiRework: 'Redução de Retrabalho',
    kpiReworkDesc: 'vs. processo manual',
    kpiDuplicates: 'Duplicatas Evitadas',
    kpiDuplicatesDesc: 'de ideias analisadas',
    kpiCollaboration: 'Participação de Colaboradores',
    kpiCollaborationDesc: 'taxa de adoção',
    kpiAiAdoption: 'Adoção de IA',
    kpiAiAdoptionDesc: 'ideias validadas por IA',
    sectionDuplication: 'Métricas de Duplicação e Controle',
    totalIdeas: 'Total de Ideias',
    duplicatesDetected: 'Duplicatas Detectadas',
    costAvoided: 'Custo Evitado (USD)',
    avgSimilarity: 'Similaridade Média',
    sectionAdoption: 'Adoção e Utilização de IA',
    ideasValidatedAI: 'Ideias Validadas com IA',
    of: 'de',
    agentAssisted: 'Validações Assistidas por Agente',
    avgQuestionsPerIdea: 'Média de Perguntas por Ideia',
    validationPatterns: 'Padrões de Validação',
    sectionProduction: 'Impacto na Produção',
    ideasInProd: 'Ideias em Produção',
    annualValue: 'Valor Anual Estimado',
    hoursSaved: 'Horas Economizadas Anualmente',
    successRate: 'Taxa de Sucesso',
    topByValue: 'Top Ideias por Valor',
    sectionROI: 'ROI e Investimento em IA',
    annualInvestment: 'Investimento Anual',
    annualValueGenerated: 'Valor Gerado Anualmente',
    roi: 'ROI %',
    payback: 'Período de Retorno',
    months: 'meses',
    sectionCollaborators: 'Melhores Colaboradores',
    colName: 'Nome',
    colIdeasSubmitted: 'Ideias Enviadas',
    colApproved: 'Aprovadas',
    colParticipation: 'Participação %',
    colLastContrib: 'Última Contribuição',
    sectionTrends: 'Tendências Mensais',
    trendSubmitted: 'Ideias Enviadas por Mês',
    trendApproved: 'Ideias Aprovadas por Mês',
    trendCost: 'Custo Mensal de IA',
    trendTotal: 'Total',
    trendAvg: 'Média',
    trendAnnual: 'Total anual',
    footerMsg: 'Painel atualizado em tempo real. Última atualização',
    loading: 'Carregando métricas executivas...',
  },
};

interface ExecutiveDashboardData {
  duplicates_avoided_percentage: number;
  retwork_reduction_percentage: number;
  collaborator_participation_rate: number;
  ai_adoption_rate: number;
  duplication_metrics: any;
  adoption_metrics: any;
  production_metrics: any;
  roi_metrics: any;
  top_collaborators: any[];
  monthly_ideas_submitted: number[];
  monthly_ideas_approved: number[];
  monthly_ai_cost: number[];
}

interface Props {
  lang?: string;
}

export default function ExecutiveDashboard({ lang = 'es' }: Props) {
  const [metrics, setMetrics] = useState<ExecutiveDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState('current');
  const t = i18n[lang] || i18n.es;
  const locale = lang === 'pt' ? 'pt-BR' : lang === 'en' ? 'en-US' : 'es-ES';

  useEffect(() => {
    fetchMetrics();
  }, [selectedPeriod]);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('aihub_demo_token');
      const url = `${API_URL}/admin/metrics/executive-dashboard?period=${selectedPeriod}`;
      
      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      setMetrics(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error loading dashboard');
      console.error('Dashboard error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>{t.loading}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>Error: {error}</div>
      </div>
    );
  }

  if (!metrics) {
    return (
      <div className={styles.container}>
        <div className={styles.error}>No data available</div>
      </div>
    );
  }

  return (
    <div className={styles.dashboardContainer}>
      <div className={styles.header}>
        <h1>{t.title}</h1>
        <div className={styles.periodSelector}>
          <select value={selectedPeriod} onChange={(e) => setSelectedPeriod(e.target.value)}>
            <option value="current">{t.periodCurrent}</option>
            <option value="last_quarter">{t.periodLastQuarter}</option>
            <option value="last_year">{t.periodLastYear}</option>
          </select>
        </div>
      </div>

      {/* KPIs Principales */}
      <div className={styles.kpiGrid}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiLabel}>{t.kpiRework}</div>
          <div className={styles.kpiValue}>{metrics.retwork_reduction_percentage.toFixed(1)}%</div>
          <div className={styles.kpiDescription}>{t.kpiReworkDesc}</div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiLabel}>{t.kpiDuplicates}</div>
          <div className={styles.kpiValue}>{metrics.duplicates_avoided_percentage.toFixed(1)}%</div>
          <div className={styles.kpiDescription}>{t.kpiDuplicatesDesc}</div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiLabel}>{t.kpiCollaboration}</div>
          <div className={styles.kpiValue}>{metrics.collaborator_participation_rate.toFixed(1)}%</div>
          <div className={styles.kpiDescription}>{t.kpiCollaborationDesc}</div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiLabel}>{t.kpiAiAdoption}</div>
          <div className={styles.kpiValue}>{metrics.ai_adoption_rate.toFixed(1)}%</div>
          <div className={styles.kpiDescription}>{t.kpiAiAdoptionDesc}</div>
        </div>
      </div>

      {/* Métricas de Duplicación */}
      <section className={styles.section}>
        <h2>{t.sectionDuplication}</h2>
        <div className={styles.metricsGrid}>
          <div className={styles.metricBox}>
            <h3>{t.totalIdeas}</h3>
            <p className={styles.metricValue}>
              {metrics.duplication_metrics.total_ideas_submitted}
            </p>
          </div>
          <div className={styles.metricBox}>
            <h3>{t.duplicatesDetected}</h3>
            <p className={styles.metricValue}>
              {metrics.duplication_metrics.duplicates_detected}
            </p>
          </div>
          <div className={styles.metricBox}>
            <h3>{t.costAvoided}</h3>
            <p className={styles.metricValue}>
              ${(metrics.duplication_metrics.duplicates_avoided_cost / 1000).toFixed(0)}K
            </p>
          </div>
          <div className={styles.metricBox}>
            <h3>{t.avgSimilarity}</h3>
            <p className={styles.metricValue}>
              {metrics.duplication_metrics.avg_similarity_score.toFixed(1)}%
            </p>
          </div>
        </div>
      </section>

      {/* Adopción de IA */}
      <section className={styles.section}>
        <h2>{t.sectionAdoption}</h2>
        <div className={styles.metricsGrid}>
          <div className={styles.metricBox}>
            <h3>{t.ideasValidatedAI}</h3>
            <p className={styles.metricValue}>
              {metrics.adoption_metrics.ideas_using_ai_validation} {t.of} {metrics.adoption_metrics.ideas_total}
            </p>
          </div>
          <div className={styles.metricBox}>
            <h3>{t.agentAssisted}</h3>
            <p className={styles.metricValue}>
              {metrics.adoption_metrics.agent_assisted_validations}
            </p>
          </div>
          <div className={styles.metricBox}>
            <h3>{t.avgQuestionsPerIdea}</h3>
            <p className={styles.metricValue}>
              {metrics.adoption_metrics.avg_agent_questions_per_idea.toFixed(1)}
            </p>
          </div>
          <div className={styles.metricBox}>
            <h3>{t.validationPatterns}</h3>
            <ul className={styles.patternList}>
              {metrics.adoption_metrics.common_validation_patterns.map(
                (pattern: string, idx: number) => (
                  <li key={idx}>{pattern}</li>
                )
              )}
            </ul>
          </div>
        </div>
      </section>

      {/* Producción y Valor */}
      <section className={styles.section}>
        <h2>{t.sectionProduction}</h2>
        <div className={styles.metricsGrid}>
          <div className={styles.metricBox}>
            <h3>{t.ideasInProd}</h3>
            <p className={styles.metricValue}>
              {metrics.production_metrics.ideas_in_production}
            </p>
          </div>
          <div className={styles.metricBox}>
            <h3>{t.annualValue}</h3>
            <p className={styles.metricValue}>
              ${(metrics.production_metrics.estimated_annual_value / 1_000_000).toFixed(1)}M
            </p>
          </div>
          <div className={styles.metricBox}>
            <h3>{t.hoursSaved}</h3>
            <p className={styles.metricValue}>
              {(metrics.production_metrics.estimated_hours_saved_annually / 1000).toFixed(0)}K
            </p>
          </div>
          <div className={styles.metricBox}>
            <h3>{t.successRate}</h3>
            <p className={styles.metricValue}>
              {metrics.production_metrics.deployment_success_rate.toFixed(1)}%
            </p>
          </div>
        </div>

        {metrics.production_metrics.top_performing_ideas.length > 0 && (
          <div className={styles.topPerformers}>
            <h3>{t.topByValue}</h3>
            <ul>
              {metrics.production_metrics.top_performing_ideas.map(
                (idea: any, idx: number) => (
                  <li key={idx}>
                    <strong>{idea.title}</strong> - ${(idea.estimated_annual_value / 1000).toFixed(0)}K
                  </li>
                )
              )}
            </ul>
          </div>
        )}
      </section>

      {/* ROI e Inversión */}
      <section className={styles.section}>
        <h2>{t.sectionROI}</h2>
        <div className={styles.roiGrid}>
          <div className={styles.roiCard}>
            <h3>{t.annualInvestment}</h3>
            <p className={styles.roiValue}>
              ${(metrics.roi_metrics.total_ai_investment_usd / 1000).toFixed(0)}K
            </p>
          </div>
          <div className={styles.roiCard}>
            <h3>{t.annualValueGenerated}</h3>
            <p className={styles.roiValue}>
              ${(metrics.roi_metrics.estimated_annual_value_generated / 1_000_000).toFixed(2)}M
            </p>
          </div>
          <div className={styles.roiCard}>
            <h3>{t.roi}</h3>
            <p className={styles.roiValue}>
              {metrics.roi_metrics.roi_percentage.toFixed(0)}%
            </p>
          </div>
          <div className={styles.roiCard}>
            <h3>{t.payback}</h3>
            <p className={styles.roiValue}>
              {metrics.roi_metrics.payback_period_months.toFixed(1)} {t.months}
            </p>
          </div>
        </div>
      </section>

      {/* Colaboradores Top */}
      <section className={styles.section}>
        <h2>{t.sectionCollaborators}</h2>
        <div className={styles.collaboratorsTable}>
          <table>
            <thead>
              <tr>
                <th>{t.colName}</th>
                <th>{t.colIdeasSubmitted}</th>
                <th>{t.colApproved}</th>
                <th>{t.colParticipation}</th>
                <th>{t.colLastContrib}</th>
              </tr>
            </thead>
            <tbody>
              {metrics.top_collaborators.map((collab: any, idx: number) => (
                <tr key={idx}>
                  <td>{collab.display_name}</td>
                  <td>{collab.ideas_submitted}</td>
                  <td>{collab.ideas_approved}</td>
                  <td>{collab.participation_rate.toFixed(1)}%</td>
                  <td>
                    {collab.last_submission
                      ? new Date(collab.last_submission).toLocaleDateString(locale)
                      : '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* Tendencias */}
      <section className={styles.section}>
        <h2>{t.sectionTrends}</h2>
        <div className={styles.trendsGrid}>
          <div className={styles.trendCard}>
            <h3>{t.trendSubmitted}</h3>
            <div className={styles.sparkline}>
              {metrics.monthly_ideas_submitted.map((val, idx) => (
                <div key={idx} className={styles.bar} style={{height: `${(val / 10) * 100}%`}} />
              ))}
            </div>
            <p>{t.trendTotal}: {metrics.monthly_ideas_submitted.reduce((a, b) => a + b, 0)}</p>
          </div>
          <div className={styles.trendCard}>
            <h3>{t.trendApproved}</h3>
            <div className={styles.sparkline}>
              {metrics.monthly_ideas_approved.map((val, idx) => (
                <div key={idx} className={styles.bar} style={{height: `${(val / 10) * 100}%`}} />
              ))}
            </div>
            <p>{t.trendTotal}: {metrics.monthly_ideas_approved.reduce((a, b) => a + b, 0)}</p>
          </div>
          <div className={styles.trendCard}>
            <h3>{t.trendCost}</h3>
            <div className={styles.costSummary}>
              <p>{t.trendAvg}: ${(metrics.monthly_ai_cost[0]).toFixed(0)}/{t.months === 'months' ? 'mo' : t.months === 'meses' ? 'mes' : 'mês'}</p>
              <p>{t.trendAnnual}: ${(metrics.monthly_ai_cost.reduce((a, b) => a + b, 0)).toFixed(0)}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Nota de actualización */}
      <div className={styles.footer}>
        <p>{t.footerMsg}: {new Date().toLocaleString(locale)}</p>
      </div>
    </div>
  );
}
