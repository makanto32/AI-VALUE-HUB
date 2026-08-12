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
    helpRework: 'Formula: 100 - (tasa de duplicados / 2). La tasa de duplicados es el porcentaje de ideas con al menos otra idea similar por encima del 60%. Representa el retrabajo evitado frente a un analisis manual.',
    helpDuplicates: 'Ideas con al menos una idea similar (similitud > 60%) dividido entre el total de ideas del tenant, expresado en porcentaje y limitado a 100%.',
    helpCollaboration: 'Promedio de la tasa de participacion de los 5 colaboradores mas activos. La tasa de cada persona es sus ideas enviadas sobre el total de ideas del tenant.',
    helpAiAdoption: 'Ideas con validacion tecnica registrada o con preguntas tecnicas generadas, dividido entre el total de ideas.',
    helpTotalIdeas: 'Conteo de todas las ideas almacenadas para el tenant, sin importar su estado.',
    helpDuplicatesDetected: 'Numero de ideas para las que existe al menos otra idea con similitud mayor al 60%, calculada por coincidencia de terminos en titulo y problema.',
    helpCostAvoided: 'Duplicados detectados multiplicados por 2.000 USD, valor asumido del esfuerzo de analisis que se evita al no reprocesar una idea repetida.',
    helpAvgSimilarity: 'Promedio de similitud entre todos los pares de ideas con coincidencia mayor a cero, acotado a 100%.',
    helpIdeasValidatedAI: 'Ideas que tienen validacion tecnica registrada o preguntas tecnicas generadas por el agente, sobre el total de ideas.',
    helpAgentAssisted: 'Ideas que registraron al menos una interaccion de clarificacion con el agente.',
    helpAvgQuestionsPerIdea: 'Suma de preguntas de clarificacion y preguntas tecnicas de todas las ideas, dividida entre el numero total de ideas.',
    helpValidationPatterns: 'Patrones derivados del analisis agregado de las validaciones registradas (temas recurrentes en preguntas y supuestos).',
    helpIdeasInProd: 'Ideas cuyo estado de despliegue es produccion.',
    helpAnnualValue: 'Para cada idea en produccion: (score de valor de negocio / 100) x 80.000 USD. Es una estimacion de valor de primer ano y se suma para todo el portafolio.',
    helpHoursSaved: 'Ideas con validacion tecnica x 8 horas de validacion manual evitada x 12 meses.',
    helpSuccessRate: 'Ideas en produccion dividido entre el total de ideas del tenant.',
    helpAnnualInvestment: 'Inversion anual configurada para la plataforma (valor por defecto 100.000 USD). Se desglosa en costo de plataforma y equivalente de consultoria.',
    helpAnnualValueGenerated: 'Suma de tres componentes: ahorro por horas evitadas (horas x 150 USD), costo evitado por duplicados y valor anual estimado de las ideas en produccion.',
    helpRoi: 'Formula: (valor generado - inversion anual) / inversion anual x 100.',
    helpPayback: 'Formula: inversion anual dividida entre el valor mensual promedio (valor generado / 12).',
    helpCollaboratorsTable: 'Ideas agrupadas por propietario. Aprobadas son las ideas con estado viable de negocio; la participacion es ideas del colaborador sobre el total del tenant.',
    helpTrends: 'Conteo de ideas por mes segun su fecha de creacion (enviadas) y su fecha de actualizacion al quedar viables (aprobadas). El costo mensual usa el costo fijo de plataforma.',
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
    helpRework: 'Formula: 100 - (duplicate rate / 2). The duplicate rate is the share of ideas that have at least one similar idea above 60%. It represents rework avoided versus a manual analysis.',
    helpDuplicates: 'Ideas with at least one similar idea (similarity > 60%) divided by the total ideas of the tenant, expressed as a percentage and capped at 100%.',
    helpCollaboration: 'Average participation rate of the top 5 collaborators. Each person rate is their submitted ideas over the tenant total.',
    helpAiAdoption: 'Ideas with a recorded technical validation or generated technical questions, divided by the total number of ideas.',
    helpTotalIdeas: 'Count of every idea stored for the tenant, regardless of status.',
    helpDuplicatesDetected: 'Number of ideas for which another idea exists with more than 60% similarity, computed from term overlap in title and problem statement.',
    helpCostAvoided: 'Detected duplicates multiplied by USD 2,000, the assumed analysis effort avoided by not reprocessing a repeated idea.',
    helpAvgSimilarity: 'Average similarity across all idea pairs with a non-zero match, capped at 100%.',
    helpIdeasValidatedAI: 'Ideas with a recorded technical validation or agent-generated technical questions, over the total number of ideas.',
    helpAgentAssisted: 'Ideas that recorded at least one clarification interaction with the agent.',
    helpAvgQuestionsPerIdea: 'Sum of clarification and technical questions across all ideas, divided by the total number of ideas.',
    helpValidationPatterns: 'Patterns derived from the aggregated analysis of recorded validations (recurring themes in questions and assumptions).',
    helpIdeasInProd: 'Ideas whose deployment status is production.',
    helpAnnualValue: 'For each idea in production: (business value score / 100) x USD 80,000. It is a first-year estimate summed across the portfolio.',
    helpHoursSaved: 'Ideas with technical validation x 8 hours of manual validation avoided x 12 months.',
    helpSuccessRate: 'Ideas in production divided by the total number of ideas in the tenant.',
    helpAnnualInvestment: 'Configured annual platform investment (default USD 100,000). It is broken down into platform cost and consulting equivalent.',
    helpAnnualValueGenerated: 'Sum of three components: savings from avoided hours (hours x USD 150), avoided duplicate cost, and estimated annual value of ideas in production.',
    helpRoi: 'Formula: (value generated - annual investment) / annual investment x 100.',
    helpPayback: 'Formula: annual investment divided by the average monthly value (value generated / 12).',
    helpCollaboratorsTable: 'Ideas grouped by owner. Approved counts ideas with business viable status; participation is the collaborator ideas over the tenant total.',
    helpTrends: 'Idea counts per month based on creation date (submitted) and update date when they became viable (approved). Monthly cost uses the fixed platform cost.',
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
    helpRework: 'Formula: 100 - (taxa de duplicatas / 2). A taxa de duplicatas e a proporcao de ideias com pelo menos outra ideia similar acima de 60%. Representa o retrabalho evitado frente a uma analise manual.',
    helpDuplicates: 'Ideias com pelo menos uma ideia similar (similaridade > 60%) divididas pelo total de ideias do tenant, em porcentagem e limitado a 100%.',
    helpCollaboration: 'Media da taxa de participacao dos 5 colaboradores mais ativos. A taxa de cada pessoa e suas ideias enviadas sobre o total do tenant.',
    helpAiAdoption: 'Ideias com validacao tecnica registrada ou com perguntas tecnicas geradas, divididas pelo total de ideias.',
    helpTotalIdeas: 'Contagem de todas as ideias armazenadas para o tenant, independentemente do status.',
    helpDuplicatesDetected: 'Numero de ideias para as quais existe outra ideia com similaridade maior que 60%, calculada pela coincidencia de termos no titulo e no problema.',
    helpCostAvoided: 'Duplicatas detectadas multiplicadas por USD 2.000, valor assumido do esforco de analise evitado ao nao reprocessar uma ideia repetida.',
    helpAvgSimilarity: 'Media de similaridade entre todos os pares de ideias com coincidencia maior que zero, limitada a 100%.',
    helpIdeasValidatedAI: 'Ideias com validacao tecnica registrada ou perguntas tecnicas geradas pelo agente, sobre o total de ideias.',
    helpAgentAssisted: 'Ideias que registraram ao menos uma interacao de clarificacao com o agente.',
    helpAvgQuestionsPerIdea: 'Soma das perguntas de clarificacao e tecnicas de todas as ideias, dividida pelo numero total de ideias.',
    helpValidationPatterns: 'Padroes derivados da analise agregada das validacoes registradas (temas recorrentes em perguntas e premissas).',
    helpIdeasInProd: 'Ideias cujo status de implantacao e producao.',
    helpAnnualValue: 'Para cada ideia em producao: (score de valor de negocio / 100) x USD 80.000. E uma estimativa de primeiro ano somada para todo o portfolio.',
    helpHoursSaved: 'Ideias com validacao tecnica x 8 horas de validacao manual evitada x 12 meses.',
    helpSuccessRate: 'Ideias em producao divididas pelo total de ideias do tenant.',
    helpAnnualInvestment: 'Investimento anual configurado para a plataforma (padrao USD 100.000). Desdobra-se em custo de plataforma e equivalente de consultoria.',
    helpAnnualValueGenerated: 'Soma de tres componentes: economia por horas evitadas (horas x USD 150), custo evitado por duplicatas e valor anual estimado das ideias em producao.',
    helpRoi: 'Formula: (valor gerado - investimento anual) / investimento anual x 100.',
    helpPayback: 'Formula: investimento anual dividido pelo valor mensal medio (valor gerado / 12).',
    helpCollaboratorsTable: 'Ideias agrupadas por proprietario. Aprovadas sao as ideias com status viavel de negocio; a participacao e as ideias do colaborador sobre o total do tenant.',
    helpTrends: 'Contagem de ideias por mes conforme a data de criacao (enviadas) e a data de atualizacao ao ficarem viaveis (aprovadas). O custo mensal usa o custo fixo de plataforma.',
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
        <div className={`${styles.kpiCard} ${styles.tooltipHost}`} data-tooltip={t.helpRework} tabIndex={0}>
          <div className={styles.kpiLabel}>{t.kpiRework}</div>
          <div className={styles.kpiValue}>{metrics.retwork_reduction_percentage.toFixed(1)}%</div>
          <div className={styles.kpiDescription}>{t.kpiReworkDesc}</div>
        </div>

        <div className={`${styles.kpiCard} ${styles.tooltipHost}`} data-tooltip={t.helpDuplicates} tabIndex={0}>
          <div className={styles.kpiLabel}>{t.kpiDuplicates}</div>
          <div className={styles.kpiValue}>{metrics.duplicates_avoided_percentage.toFixed(1)}%</div>
          <div className={styles.kpiDescription}>{t.kpiDuplicatesDesc}</div>
        </div>

        <div className={`${styles.kpiCard} ${styles.tooltipHost}`} data-tooltip={t.helpCollaboration} tabIndex={0}>
          <div className={styles.kpiLabel}>{t.kpiCollaboration}</div>
          <div className={styles.kpiValue}>{metrics.collaborator_participation_rate.toFixed(1)}%</div>
          <div className={styles.kpiDescription}>{t.kpiCollaborationDesc}</div>
        </div>

        <div className={`${styles.kpiCard} ${styles.tooltipHost}`} data-tooltip={t.helpAiAdoption} tabIndex={0}>
          <div className={styles.kpiLabel}>{t.kpiAiAdoption}</div>
          <div className={styles.kpiValue}>{metrics.ai_adoption_rate.toFixed(1)}%</div>
          <div className={styles.kpiDescription}>{t.kpiAiAdoptionDesc}</div>
        </div>
      </div>

      {/* Métricas de Duplicación */}
      <section className={styles.section}>
        <h2>{t.sectionDuplication}</h2>
        <div className={styles.metricsGrid}>
          <div className={`${styles.metricBox} ${styles.tooltipHost}`} data-tooltip={t.helpTotalIdeas} tabIndex={0}>
            <h3>{t.totalIdeas}</h3>
            <p className={styles.metricValue}>
              {metrics.duplication_metrics.total_ideas_submitted}
            </p>
          </div>
          <div className={`${styles.metricBox} ${styles.tooltipHost}`} data-tooltip={t.helpDuplicatesDetected} tabIndex={0}>
            <h3>{t.duplicatesDetected}</h3>
            <p className={styles.metricValue}>
              {metrics.duplication_metrics.duplicates_detected}
            </p>
          </div>
          <div className={`${styles.metricBox} ${styles.tooltipHost}`} data-tooltip={t.helpCostAvoided} tabIndex={0}>
            <h3>{t.costAvoided}</h3>
            <p className={styles.metricValue}>
              ${(metrics.duplication_metrics.duplicates_avoided_cost / 1000).toFixed(0)}K
            </p>
          </div>
          <div className={`${styles.metricBox} ${styles.tooltipHost}`} data-tooltip={t.helpAvgSimilarity} tabIndex={0}>
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
          <div className={`${styles.metricBox} ${styles.tooltipHost}`} data-tooltip={t.helpIdeasValidatedAI} tabIndex={0}>
            <h3>{t.ideasValidatedAI}</h3>
            <p className={styles.metricValue}>
              {metrics.adoption_metrics.ideas_using_ai_validation} {t.of} {metrics.adoption_metrics.ideas_total}
            </p>
          </div>
          <div className={`${styles.metricBox} ${styles.tooltipHost}`} data-tooltip={t.helpAgentAssisted} tabIndex={0}>
            <h3>{t.agentAssisted}</h3>
            <p className={styles.metricValue}>
              {metrics.adoption_metrics.agent_assisted_validations}
            </p>
          </div>
          <div className={`${styles.metricBox} ${styles.tooltipHost}`} data-tooltip={t.helpAvgQuestionsPerIdea} tabIndex={0}>
            <h3>{t.avgQuestionsPerIdea}</h3>
            <p className={styles.metricValue}>
              {metrics.adoption_metrics.avg_agent_questions_per_idea.toFixed(1)}
            </p>
          </div>
          <div className={`${styles.metricBox} ${styles.tooltipHost}`} data-tooltip={t.helpValidationPatterns} tabIndex={0}>
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
          <div className={`${styles.metricBox} ${styles.tooltipHost}`} data-tooltip={t.helpIdeasInProd} tabIndex={0}>
            <h3>{t.ideasInProd}</h3>
            <p className={styles.metricValue}>
              {metrics.production_metrics.ideas_in_production}
            </p>
          </div>
          <div className={`${styles.metricBox} ${styles.tooltipHost}`} data-tooltip={t.helpAnnualValue} tabIndex={0}>
            <h3>{t.annualValue}</h3>
            <p className={styles.metricValue}>
              ${(metrics.production_metrics.estimated_annual_value / 1_000_000).toFixed(1)}M
            </p>
          </div>
          <div className={`${styles.metricBox} ${styles.tooltipHost}`} data-tooltip={t.helpHoursSaved} tabIndex={0}>
            <h3>{t.hoursSaved}</h3>
            <p className={styles.metricValue}>
              {(metrics.production_metrics.estimated_hours_saved_annually / 1000).toFixed(0)}K
            </p>
          </div>
          <div className={`${styles.metricBox} ${styles.tooltipHost}`} data-tooltip={t.helpSuccessRate} tabIndex={0}>
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
          <div className={`${styles.roiCard} ${styles.tooltipHost}`} data-tooltip={t.helpAnnualInvestment} tabIndex={0}>
            <h3>{t.annualInvestment}</h3>
            <p className={styles.roiValue}>
              ${(metrics.roi_metrics.total_ai_investment_usd / 1000).toFixed(0)}K
            </p>
          </div>
          <div className={`${styles.roiCard} ${styles.tooltipHost}`} data-tooltip={t.helpAnnualValueGenerated} tabIndex={0}>
            <h3>{t.annualValueGenerated}</h3>
            <p className={styles.roiValue}>
              ${(metrics.roi_metrics.estimated_annual_value_generated / 1_000_000).toFixed(2)}M
            </p>
          </div>
          <div className={`${styles.roiCard} ${styles.tooltipHost}`} data-tooltip={t.helpRoi} tabIndex={0}>
            <h3>{t.roi}</h3>
            <p className={styles.roiValue}>
              {metrics.roi_metrics.roi_percentage.toFixed(0)}%
            </p>
          </div>
          <div className={`${styles.roiCard} ${styles.tooltipHost}`} data-tooltip={t.helpPayback} tabIndex={0}>
            <h3>{t.payback}</h3>
            <p className={styles.roiValue}>
              {metrics.roi_metrics.payback_period_months.toFixed(1)} {t.months}
            </p>
          </div>
        </div>
      </section>

      {/* Colaboradores Top */}
      <section className={styles.section}>
        <h2 className={styles.tooltipHost} data-tooltip={t.helpCollaboratorsTable} tabIndex={0}>{t.sectionCollaborators}</h2>
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
        <h2 className={styles.tooltipHost} data-tooltip={t.helpTrends} tabIndex={0}>{t.sectionTrends}</h2>
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
