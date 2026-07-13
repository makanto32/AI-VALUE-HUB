# Prompt Guide: Token Optimization (ES/EN)

## 1) Version en Espanol

### Formato de campos para "Nueva idea" (alineado al formulario actual)
Campos esperados:
- title
- problem_statement
- expected_value
- affected_users (lista separada por coma)
- source_language (es|en|pt)

Nota:
- tenant_id lo toma la aplicacion desde la sesion autenticada, no se captura manualmente en el prompt.

Plantilla recomendada (token-efficient):
```text
title: <3 a 120 caracteres, concreto>
problem_statement: <10 a 450 caracteres, problema observable y actual>
expected_value: <5 a 300 caracteres, impacto medible>
affected_users: <area1, area2, area3>
source_language: <es|en|pt>
```

Ejemplo optimo (ES):
```text
title: Deteccion temprana de fraude en onboarding digital
problem_statement: El equipo de riesgo revisa manualmente demasiados casos en onboarding, generando atrasos y falsos positivos.
expected_value: Reducir 25% el tiempo de revision y 15% los falsos positivos en 8 semanas de piloto.
affected_users: riesgo, operaciones, cumplimiento
source_language: es
```

Ejemplo deficiente (ES):
```text
title: IA banco
problem_statement: Queremos mejorar todo lo del onboarding, fraude y eficiencia cuanto antes.
expected_value: Que todo sea mejor y mas rapido.
affected_users: todos
source_language: es
```

Analisis rapido (formato de campos):
1. title:
- Optimo: especifico y enfocado en un problema.
- Deficiente: ambiguo y sin alcance.
2. problem_statement:
- Optimo: describe situacion actual y dolor operativo.
- Deficiente: generalista, sin contexto util.
3. expected_value:
- Optimo: incluye metricas y horizonte temporal.
- Deficiente: no medible.
4. affected_users:
- Optimo: equipos concretos.
- Deficiente: "todos" no ayuda a priorizar.
5. source_language:
- Optimo y deficiente: valido si usa es|en|pt; la diferencia real esta en calidad de contenido.

### Prompt optimo (token-efficient)
Actua como analista de innovacion empresarial. Evalua esta idea y responde en maximo 220 palabras.

Contexto minimo:
- Empresa: banco retail en Latam
- Objetivo: reducir fraude en onboarding digital
- Restricciones: cumplimiento KYC/AML, sin cambiar core bancario en fase inicial
- Horizonte: piloto en 8 semanas

Idea:
"Aplicar scoring de riesgo con senales de comportamiento y validacion documental asistida por IA para priorizar casos sospechosos y reducir revision manual."

Entrega exactamente en este formato:
1) Resumen de la idea (1 frase)
2) Valor esperado (3 bullets)
3) Riesgos clave (3 bullets)
4) Viabilidad tecnica (Alta/Media/Baja + 1 frase)
5) Proximo paso recomendado (1 accion concreta)

### Prompt deficiente
Necesito que analices una idea que tenemos para mejorar muchos procesos en el banco, sobre IA, fraude, clientes, operacion, tiempos y transformacion digital. Quiero un analisis muy completo y detallado con todo lo que creas relevante: vision estrategica, tactica, operativa, tecnologica, regulatoria, roadmap, costos, riesgos, posibles integraciones, beneficios, impactos, quick wins, largo plazo, roles, metricas, KPIs, gobierno, arquitectura y cualquier otro tema que consideres. Puedes extenderte todo lo que necesites y usar el formato que prefieras.

### Analisis comparativo
1. Claridad de objetivo:
- Optimo: define rol, contexto, limites y salida exacta.
- Deficiente: pide "todo", sin foco ni criterio de priorizacion.

2. Consumo de tokens:
- Optimo: restringe longitud y estructura, reduce expansion innecesaria.
- Deficiente: invita a respuestas largas y dispersas, mayor costo.

3. Calidad operativa:
- Optimo: produce salida accionable y comparable entre ideas.
- Deficiente: salida variable, dificil de estandarizar o automatizar.

4. Tiempo de iteracion:
- Optimo: mas rapido para revisar y decidir siguiente paso.
- Deficiente: mas lento de leer, extraer y convertir en accion.

5. Riesgo de alucinacion:
- Optimo: menos espacio para inventar por falta de alcance.
- Deficiente: al abrir demasiados frentes, aumenta suposiciones.

---

## 2) English Version

### "New Idea" field format (aligned with current form)
Expected fields:
- title
- problem_statement
- expected_value
- affected_users (comma-separated list)
- source_language (es|en|pt)

Note:
- tenant_id is taken from the authenticated session by the app; it is not manually entered in the prompt.

Recommended template (token-efficient):
```text
title: <3 to 120 chars, specific>
problem_statement: <10 to 450 chars, observable current pain>
expected_value: <5 to 300 chars, measurable outcome>
affected_users: <team1, team2, team3>
source_language: <es|en|pt>
```

Optimal example (EN):
```text
title: Early fraud detection in digital onboarding
problem_statement: The risk team manually reviews too many onboarding cases, causing delays and false positives.
expected_value: Reduce review time by 25% and false positives by 15% in an 8-week pilot.
affected_users: risk, operations, compliance
source_language: en
```

Poor example (EN):
```text
title: AI for bank
problem_statement: We want to improve everything in onboarding, fraud, and efficiency as soon as possible.
expected_value: Make everything better and faster.
affected_users: everyone
source_language: en
```

Quick analysis (field format):
1. title:
- Optimal: specific and scoped.
- Poor: vague and broad.
2. problem_statement:
- Optimal: concrete current-state pain.
- Poor: generic, low signal.
3. expected_value:
- Optimal: measurable target plus timeline.
- Poor: not measurable.
4. affected_users:
- Optimal: concrete teams.
- Poor: "everyone" prevents prioritization.
5. source_language:
- Both can be valid if using es|en|pt; the real difference is content quality.

### Optimal prompt (token-efficient)
Act as an enterprise innovation analyst. Evaluate this idea and answer in no more than 220 words.

Minimal context:
- Company: retail bank in LatAm
- Goal: reduce fraud in digital onboarding
- Constraints: KYC/AML compliance, no core banking replacement in initial phase
- Timeline: 8-week pilot

Idea:
"Use AI-assisted risk scoring with behavioral signals and document validation to prioritize suspicious cases and reduce manual review workload."

Return exactly in this format:
1) Idea summary (1 sentence)
2) Expected value (3 bullets)
3) Key risks (3 bullets)
4) Technical feasibility (High/Medium/Low + 1 sentence)
5) Recommended next step (1 concrete action)

### Poor prompt
Please analyze an idea we have to improve many banking processes related to AI, fraud, customer experience, operations, speed, and digital transformation. I want a very complete and detailed analysis covering everything you think is relevant: strategic vision, tactical and operational planning, technology, regulatory aspects, roadmap, costs, risks, integrations, benefits, impacts, quick wins, long-term opportunities, roles, metrics, KPIs, governance, architecture, and anything else you can think of. Feel free to be as long as needed and use any format you prefer.

### Comparative analysis
1. Objective clarity:
- Optimal: clear role, context, boundaries, and output format.
- Poor: asks for "everything," with no prioritization criteria.

2. Token usage:
- Optimal: length cap and fixed structure prevent unnecessary expansion.
- Poor: encourages long, unfocused output and higher cost.

3. Operational quality:
- Optimal: actionable and easy to compare across ideas.
- Poor: inconsistent output, hard to standardize or automate.

4. Iteration speed:
- Optimal: faster to review and decide next actions.
- Poor: slower to read, extract, and operationalize.

5. Hallucination risk:
- Optimal: less room for unsupported assumptions.
- Poor: broader scope increases speculative content.

---

## 3) Demo Examples for UI "New Idea" (EN/ES/PT)

Use these examples directly in the UI form with this exact field structure:
- title
- problem_statement
- expected_value
- affected_users
- source_language

### A. Examples likely to pass business viability

#### A1) English (viable)
```text
title: AI-assisted KYC anomaly triage for digital onboarding
problem_statement: The risk team manually reviews all onboarding alerts, creating long queues and inconsistent decisions during peak periods.
expected_value: Reduce manual review time by 30% and false positives by 18% in a 10-week pilot while keeping KYC/AML controls.
affected_users: risk, operations, compliance
source_language: en
```

#### A2) Espanol (viable)
```text
title: Priorizacion inteligente de alertas de fraude en onboarding
problem_statement: En onboarding digital, el equipo de riesgo revisa alertas de forma manual y tarda demasiado en resolver casos de bajo riesgo.
expected_value: Reducir 28% el tiempo promedio de revision y 15% los falsos positivos en 2 meses, manteniendo controles KYC.
affected_users: riesgo, operaciones, cumplimiento
source_language: es
```

#### A3) Portugues (viable)
```text
title: Priorizacao de alertas de fraude no onboarding digital
problem_statement: O time de risco analisa alertas manualmente no onboarding, com alto volume e baixa padronizacao de decisao.
expected_value: Reduzir em 25% o tempo de analise e em 12% os falsos positivos em 8 semanas, sem reduzir controles de compliance.
affected_users: risco, operacoes, compliance
source_language: pt
```

### B. Examples likely to require more information (clarification)

#### B1) English (needs more info)
```text
title: Improve onboarding quality with AI recommendations
problem_statement: We think onboarding could be better with AI guidance, but we still do not know which cases should be prioritized first.
expected_value: Better performance and faster reviews, to be defined after initial exploration.
affected_users: risk, operations
source_language: en
```

#### B2) Espanol (requiere mas informacion)
```text
title: Mejorar decisiones de onboarding con apoyo de IA
problem_statement: Queremos apoyar al equipo con IA en onboarding, pero aun no tenemos claro que reglas, datos y umbrales se deben usar.
expected_value: Mejorar tiempos y calidad de decision, pendiente definir metrica concreta y alcance por canal.
affected_users: riesgo, operaciones
source_language: es
```

#### B3) Portugues (requer mais informacao)
```text
title: Apoio de IA para decisao em onboarding
problem_statement: Existe interesse em usar IA no onboarding, mas ainda ha duvida sobre dados disponiveis, criterios de priorizacao e controles.
expected_value: Ganho de eficiencia e melhor qualidade de analise, com metas a definir apos levantamento inicial.
affected_users: risco, operacoes
source_language: pt
```

### Practical notes for demo behavior
1. Viable examples include clearer metrics, timeline, and regulated context (KYC/compliance), which usually improves business viability scoring.
2. Clarification examples keep real business intent but leave key evidence open (exact KPI baseline, thresholds, or data readiness), so they are better candidates for "needs more information" in demo flows.
