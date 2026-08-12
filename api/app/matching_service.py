"""
Service for finding related initiatives and matching similar ideas.
Utiliza búsqueda semántica mejorada basada en palabras clave, sinónimos y análisis de intención
para detectar iniciativas relacionadas incluso cuando el wording cambia.
"""

from typing import List, Dict, Tuple
import re
from difflib import SequenceMatcher
from .models import (
    IdeaCase,
    RelatedInitiative,
    Contact,
    IdeaMatchingResult,
    InitiativeCatalog,
    DeploymentStatus,
)


# Contactos clave asociados a iniciativas
INITIATIVE_CONTACTS = {
    # Scoring de Riesgo Crediticio Avanzado (Funding)
    "modelo-scoring-riesgo": {
        "primary": Contact(
            contact_id="c-carlos-mendez",
            name="Carlos Mendez",
            email="carlos.mendez@contoso.com",
            role="Risk Team Lead",
            department="Risk Management",
            phone="+56-2-1234-5001",
        ),
        "secondary": [
            Contact(
                contact_id="c-ana-torres",
                name="Ana Torres",
                email="ana.torres@contoso.com",
                role="Risk Analyst",
                department="Risk Management",
                phone="+56-2-1234-5002",
            ),
        ],
    },
    # Onboarding Digital (Production)
    "onboarding-digital": {
        "primary": Contact(
            contact_id="c-maria-rodriguez",
            name="Maria Rodriguez",
            email="maria.rodriguez@contoso.com",
            role="Operations Director",
            department="Operations",
            phone="+56-2-1234-6001",
        ),
        "secondary": [
            Contact(
                contact_id="c-juan-lopez",
                name="Juan Lopez",
                email="juan.lopez@contoso.com",
                role="Digital Transformation Manager",
                department="Operations",
                phone="+56-2-1234-6002",
            ),
        ],
    },
    # Fraud Detection (Production)
    "fraud-detection-engine": {
        "primary": Contact(
            contact_id="c-roberto-gonzalez",
            name="Roberto Gonzalez",
            email="roberto.gonzalez@contoso.com",
            role="Security Chief",
            department="Security & Compliance",
            phone="+56-2-1234-7001",
        ),
        "secondary": [
            Contact(
                contact_id="c-patricia-silva",
                name="Patricia Silva",
                email="patricia.silva@contoso.com",
                role="Fraud Detection Specialist",
                department="Security & Compliance",
                phone="+56-2-1234-7002",
            ),
        ],
    },
}


# Mapeo de sinónimos para detectar conceptos relacionados
SEMANTIC_SYNONYMS = {
    # Predicción y detección
    "predicción": ["predictor", "predecir", "forecasting", "pronóstico", "estimación"],
    "predictor": ["predicción", "predecir", "forecasting", "pronóstico", "estimación"],
    "detección": ["detectar", "detector", "detection", "identificación", "descubrimiento"],
    "fraude": ["fraude", "fraudulento", "fraud", "estafa", "engaño"],
    "rotación": ["churn", "rotación", "abandono", "deserción", "fuga"],
    "cliente": ["cliente", "customer", "usuario", "cuenta", "suscriptor"],
    
    # Análisis y evaluación
    "análisis": ["análisis", "análitica", "analítica", "análitico", "scoring", "evaluación"],
    "scoring": ["score", "puntuación", "calificación", "rating", "evaluación"],
    "riesgo": ["riesgo", "risk", "peligro", "riesgos", "exposición"],
    
    # Automatización y procesos
    "automatización": ["automatizar", "automático", "automatizado", "automation", "automatizacion"],
    "onboarding": ["onboarding", "incorporación", "ingreso", "integración", "alta"],
    "validación": ["validar", "validación", "validation", "verificación", "confirmación"],
    
    # Machine learning
    "machine learning": ["ml", "machine learning", "aprendizaje automático", "ia", "inteligencia artificial"],
    "ai": ["ai", "machine learning", "inteligencia artificial", "ml", "aprendizaje automático"],
}


def _normalize_text_for_semantic_comparison(text: str) -> str:
    """
    Normaliza texto para comparación semántica.
    Convierte a lowercase, remove acentos, especiales, y palabras comunes.
    """
    if not text:
        return ""
    
    # Convertir a minúsculas
    text = text.lower().strip()
    
    # Remover acentos
    text = re.sub(r'á', 'a', text)
    text = re.sub(r'é', 'e', text)
    text = re.sub(r'í', 'i', text)
    text = re.sub(r'ó', 'o', text)
    text = re.sub(r'ú', 'u', text)
    
    # Remover caracteres especiales pero mantener espacios
    text = re.sub(r'[^\w\s]', '', text)
    
    # Palabras comunes a ignorar (stop words en español)
    stop_words = {
        'de', 'la', 'el', 'una', 'un', 'y', 'o', 'en', 'que', 'del', 'los', 'las',
        'es', 'para', 'por', 'con', 'a', 'al', 'son', 'sido', 'ser', 'este',
        'esta', 'estos', 'estas', 'sistema', 'nuevo', 'nueva', 'nueve',
    }
    
    # Remover stop words
    words = text.split()
    words = [w for w in words if w not in stop_words and len(w) > 2]
    
    return ' '.join(words)


def _apply_semantic_synonyms(text: str) -> List[str]:
    """
    Expande un texto con sinónimos semánticos.
    Retorna lista de palabras clave semanticamente relacionadas.
    """
    text_lower = text.lower()
    semantic_terms = set()
    
    # Buscar términos clave y agregar sus sinónimos
    for base_term, synonyms in SEMANTIC_SYNONYMS.items():
        if base_term in text_lower:
            semantic_terms.add(base_term)
            semantic_terms.update(synonyms)
    
    return list(semantic_terms)


def _calculate_string_similarity(str1: str, str2: str) -> float:
    """
    Calcula similitud entre dos strings usando SequenceMatcher.
    Retorna score de 0-100.
    """
    if not str1 or not str2:
        return 0.0
    
    # Normalizar ambas strings
    s1 = _normalize_text_for_semantic_comparison(str1)
    s2 = _normalize_text_for_semantic_comparison(str2)
    
    if not s1 or not s2:
        return 0.0
    
    # Usar SequenceMatcher para similitud estructural
    ratio = SequenceMatcher(None, s1, s2).ratio()
    return ratio * 100


def _calculate_concept_overlap(text1: str, text2: str) -> float:
    """
    Calcula solapamiento de conceptos semánticos entre dos textos.
    Usa sinónimos para detectar mismo tema con distinto wording.
    Retorna score de 0-100.
    """
    if not text1 or not text2:
        return 0.0
    
    # Obtener conceptos de ambos textos
    concepts1 = set(_apply_semantic_synonyms(text1))
    concepts2 = set(_apply_semantic_synonyms(text2))
    
    if not concepts1 or not concepts2:
        return 0.0
    
    # Intersección y unión
    intersection = len(concepts1 & concepts2)
    union = len(concepts1 | concepts2)
    
    if union == 0:
        return 0.0
    
    # Score basado en solapamiento de conceptos
    return (intersection / union) * 100


def _calculate_keyword_similarity(text1: str, text2: str) -> float:
    """
    Calcula similitud basada en palabras clave compartidas (método original).
    Retorna score de 0-100.
    """
    if not text1 or not text2:
        return 0.0

    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    intersection = len(words1 & words2)
    union = len(words1 | words2)

    if union == 0:
        return 0.0

    similarity = (intersection / union) * 100
    return min(similarity, 100.0)


def _get_keywords_for_idea(idea: IdeaCase) -> List[str]:
    """Extrae palabras clave de una idea para búsqueda."""
    keywords = []

    # Extraer palabras clave del título y problem statement
    text = f"{idea.title} {idea.problem_statement} {idea.expected_value}".lower()

    # Palabras clave específicas del dominio financiero
    financial_keywords = {
        "fraude": "fraud",
        "kyc": "kyc",
        "onboarding": "onboarding",
        "riesgo": "risk",
        "crédito": "credit",
        "documento": "document",
        "transacción": "transaction",
        "detección": "detection",
        "validación": "validation",
        "automatización": "automation",
        "chatbot": "chatbot",
        "soporte": "support",
        "scoring": "scoring",
        "machine learning": "ml",
        "inteligencia artificial": "ai",
    }

    for keyword, eng_keyword in financial_keywords.items():
        if keyword in text:
            keywords.append(keyword)
            keywords.append(eng_keyword)

    return keywords


def find_related_initiatives(
    new_idea: IdeaCase, all_ideas: List[IdeaCase]
) -> List[RelatedInitiative]:
    """
    Encuentra iniciativas relacionadas a una idea nueva usando análisis semántico robusto.
    
    Combina 4 estrategias de detección:
    1. Similitud de palabras clave directas (método original)
    2. Similitud estructural de strings (SequenceMatcher)
    3. Solapamiento de conceptos semánticos (sinónimos)
    4. Análisis de intención en problem_statement

    Args:
        new_idea: Idea nueva ingresada
        all_ideas: Lista de todas las ideas en la BD

    Returns:
        Lista de iniciativas relacionadas con score de similitud mejorado
    """
    related = []

    # Excluir la idea actual
    other_ideas = [i for i in all_ideas if i.idea_id != new_idea.idea_id]

    for existing_idea in other_ideas:
        # Solo mostrar ideas en funding o production
        if existing_idea.deployment_status not in [
            DeploymentStatus.funding,
            DeploymentStatus.production,
        ]:
            continue

        # ========== ESTRATEGIA 1: Similitud de palabras clave (original) ==========
        title_keyword_sim = _calculate_keyword_similarity(
            new_idea.title, existing_idea.title
        )
        problem_keyword_sim = _calculate_keyword_similarity(
            new_idea.problem_statement, existing_idea.problem_statement
        )
        value_keyword_sim = _calculate_keyword_similarity(
            new_idea.expected_value, existing_idea.expected_value
        )
        
        # ========== ESTRATEGIA 2: Similitud estructural (SequenceMatcher) ==========
        title_string_sim = _calculate_string_similarity(
            new_idea.title, existing_idea.title
        )
        problem_string_sim = _calculate_string_similarity(
            new_idea.problem_statement, existing_idea.problem_statement
        )
        
        # ========== ESTRATEGIA 3: Solapamiento de conceptos semánticos ==========
        title_concept_sim = _calculate_concept_overlap(
            new_idea.title, existing_idea.title
        )
        problem_concept_sim = _calculate_concept_overlap(
            new_idea.problem_statement, existing_idea.problem_statement
        )
        
        # ========== ESTRATEGIA 4: Intención combinada ==========
        # Combina title + problem para detectar intención global
        intent_similarity = _calculate_concept_overlap(
            f"{new_idea.title} {new_idea.problem_statement}",
            f"{existing_idea.title} {existing_idea.problem_statement}"
        )

        # ========== SCORE COMBINADO ==========
        # Usa máximo entre estrategias para robustez ante cambios de wording
        # Si hay alta similitud en CUALQUIER dimensión, se reporta
        
        title_sim = max(title_keyword_sim, title_string_sim, title_concept_sim)
        problem_sim = max(problem_keyword_sim, problem_string_sim, problem_concept_sim)
        value_sim = value_keyword_sim
        
        # Score final con pesos ajustados (problem es lo más importante)
        similarity_score = (
            title_sim * 0.3 + 
            problem_sim * 0.45 + 
            value_sim * 0.15 +
            intent_similarity * 0.10
        )

        # THRESHOLD CRÍTICO: si hay muy alta similitud en problema o intención,
        # potencial duplicidad incluso con bajo score general
        is_potential_duplicate = (
            problem_sim > 60 or  # Problema muy similar
            intent_similarity > 70 or  # Intención muy similar
            (title_sim > 50 and problem_sim > 30)  # Título + algún problema similar
        )
        
        if similarity_score > 12 or is_potential_duplicate:
            # Determinar match reason basado en qué dimensión fue más similar
            if is_potential_duplicate:
                if problem_sim > 60:
                    match_reason = "Resuelve problema muy similar (posible duplicidad)"
                elif intent_similarity > 70:
                    match_reason = "Intención similar con distinto wording (posible duplicidad)"
                else:
                    match_reason = "Potencial duplicidad detectada"
            elif title_sim > 50:
                match_reason = "Titulo muy similar"
            elif problem_sim > 50:
                match_reason = "Resuelve problema similar"
            elif value_sim > 40:
                match_reason = "Valor esperado relacionado"
            else:
                match_reason = "Iniciativa potencialmente complementaria"

            # Obtener contactos
            contacts_key = _find_contacts_key(existing_idea.title)
            primary_contact = None
            secondary_contacts = []

            if contacts_key and contacts_key in INITIATIVE_CONTACTS:
                contact_info = INITIATIVE_CONTACTS[contacts_key]
                primary_contact = contact_info.get("primary")
                secondary_contacts = contact_info.get("secondary", [])

            related.append(
                RelatedInitiative(
                    idea_id=existing_idea.idea_id,
                    title=existing_idea.title,
                    problem_statement=existing_idea.problem_statement,
                    deployment_status=existing_idea.deployment_status,
                    current_stage=existing_idea.current_stage,
                    status=existing_idea.status,
                    solution_name=existing_idea.architecture_package.solution_name
                    if existing_idea.architecture_package
                    else None,
                    similarity_score=similarity_score,
                    match_reason=match_reason,
                    primary_contact=primary_contact,
                    secondary_contacts=secondary_contacts,
                    estimated_go_live=_estimate_go_live(existing_idea),
                )
            )

    # Ordenar por similitud descendente
    related.sort(key=lambda x: x.similarity_score, reverse=True)
    return related[:5]  # Retornar top 5


def _find_contacts_key(idea_title: str) -> str:
    """Mapea título de idea a clave de contactos."""
    title_lower = idea_title.lower()

    if "scoring" in title_lower and "riesgo" in title_lower:
        return "modelo-scoring-riesgo"
    elif "onboarding" in title_lower and "digital" in title_lower:
        return "onboarding-digital"
    elif "fraude" in title_lower and ("detección" in title_lower or "detection" in title_lower):
        return "fraud-detection-engine"

    return None


def _estimate_go_live(idea: IdeaCase) -> str:
    """Estima fecha de go-live según deployment_status."""
    if idea.deployment_status == DeploymentStatus.production:
        return "En produccion"
    elif idea.deployment_status == DeploymentStatus.funding:
        return "Q3 2026 (estimado)"
    return "TBD"


def create_matching_result(
    new_idea: IdeaCase,
    related_initiatives: List[RelatedInitiative],
) -> IdeaMatchingResult:
    """
    Crea un resultado de matching completo para una idea nueva.

    Incluye análisis de contexto, iniciativas relacionadas, y acciones recomendadas.
    """
    # Análisis de contexto
    context_analysis = f"""
Idea ingresada: {new_idea.title}
Problema: {new_idea.problem_statement}
Impacto esperado: {new_idea.expected_value}
Usuarios afectados: {', '.join(new_idea.affected_users) if new_idea.affected_users else 'No especificado'}

Contexto empresarial:
- Empresa: {new_idea.context_snapshot.company_name if new_idea.context_snapshot else 'N/A'}
- Industria: {new_idea.context_snapshot.industry if new_idea.context_snapshot else 'N/A'}
- Tolerancia al riesgo: {new_idea.context_snapshot.risk_tolerance if new_idea.context_snapshot else 'N/A'}
"""

    # Acciones recomendadas
    recommended_actions = []
    if len(related_initiatives) > 0:
        recommended_actions.append(
            f"Existen {len(related_initiatives)} iniciativas relacionadas en desarrollo o producción."
        )
        recommended_actions.append(
            "Validar alineación y posibles oportunidades de colaboración."
        )
        recommended_actions.append(
            f"Contactar al equipo responsable para evaluar retroalimentación."
        )

    if len(related_initiatives) == 0:
        recommended_actions.append(
            "No se encontraron iniciativas similares. Idea potencialmente nueva."
        )
        recommended_actions.append(
            "Proceder a validación de negocio según flujo estándar."
        )

    # Ids de ideas para feedback
    can_provide_feedback_to = [ri.idea_id for ri in related_initiatives]

    # Determinar si requiere escalamiento
    should_escalate = (
        len(related_initiatives) > 2
        or any(ri.deployment_status == DeploymentStatus.production for ri in related_initiatives)
    )
    escalation_reason = (
        "Múltiples iniciativas relacionadas o impacto en sistemas en producción"
        if should_escalate
        else None
    )

    return IdeaMatchingResult(
        idea_id=new_idea.idea_id,
        title=new_idea.title,
        problem_statement=new_idea.problem_statement,
        context_analysis=context_analysis,
        related_initiatives=related_initiatives,
        recommended_actions=recommended_actions,
        can_provide_feedback_to=can_provide_feedback_to,
        should_escalate_to_leadership=should_escalate,
        escalation_reason=escalation_reason,
    )


def build_initiatives_catalog(all_ideas: List[IdeaCase]) -> InitiativeCatalog:
    """
    Construye catálogo de iniciativas organizadas por deployment_status.
    Solo incluye ideas en funding o production.
    """
    development = []
    funding = []
    production = []

    for idea in all_ideas:
        if idea.deployment_status not in [
            DeploymentStatus.funding,
            DeploymentStatus.production,
        ]:
            continue

        contacts_key = _find_contacts_key(idea.title)
        primary_contact = None
        secondary_contacts = []

        if contacts_key and contacts_key in INITIATIVE_CONTACTS:
            contact_info = INITIATIVE_CONTACTS[contacts_key]
            primary_contact = contact_info.get("primary")
            secondary_contacts = contact_info.get("secondary", [])

        initiative = RelatedInitiative(
            idea_id=idea.idea_id,
            title=idea.title,
            problem_statement=idea.problem_statement,
            deployment_status=idea.deployment_status,
            current_stage=idea.current_stage,
            status=idea.status,
            solution_name=idea.architecture_package.solution_name
            if idea.architecture_package
            else None,
            similarity_score=100.0,
            match_reason="Iniciativa en catálogo",
            primary_contact=primary_contact,
            secondary_contacts=secondary_contacts,
            estimated_go_live=_estimate_go_live(idea),
        )

        if idea.deployment_status == DeploymentStatus.development:
            development.append(initiative)
        elif idea.deployment_status == DeploymentStatus.funding:
            funding.append(initiative)
        elif idea.deployment_status == DeploymentStatus.production:
            production.append(initiative)

    return InitiativeCatalog(
        total_count=len(development) + len(funding) + len(production),
        development=development,
        funding=funding,
        production=production,
    )
