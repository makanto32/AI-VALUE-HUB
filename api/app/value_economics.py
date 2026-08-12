"""
Value economics service.

Builds an objective comparison between the estimated monthly run cost of the
proposed architecture and the quantified monthly business value (savings) the
idea is expected to deliver. It is used during technical validation so that an
idea that is viable in both business and technical phases can still be flagged
when its consumption cost is disproportionate to the expected value.
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

from .models import IdeaCase, ValueEconomics


# Blended fully-loaded hourly cost used when the expected value is expressed in
# saved hours instead of currency. Planning figure only.
DEFAULT_HOURLY_COST_USD = 35.0

# Fallback monthly value per affected user when no quantitative signal exists.
# Scaled by the business value score so low-scoring ideas are not overvalued.
FALLBACK_VALUE_PER_USER_USD = 90.0

# Ratio thresholds (monthly savings / monthly cost).
RATIO_STRONG = 3.0
RATIO_ACCEPTABLE = 1.5
RATIO_BREAK_EVEN = 1.0

_MULTIPLIER_WORDS = {
    "k": 1_000,
    "mil": 1_000,
    "thousand": 1_000,
    "m": 1_000_000,
    "mm": 1_000_000,
    "millon": 1_000_000,
    "millones": 1_000_000,
    "million": 1_000_000,
    "millions": 1_000_000,
    "milhao": 1_000_000,
    "milhoes": 1_000_000,
}

_PERIOD_TO_MONTHLY = [
    (r"\b(mensual|mensuales|mes|monthly|month|mensal|por mes|per month)\b", 1.0),
    (r"\b(anual|anuales|ano|año|annual|annually|year|yearly|per year|al ano|al año)\b", 1.0 / 12.0),
    (r"\b(trimestral|quarter|quarterly)\b", 1.0 / 3.0),
    (r"\b(semanal|weekly|week|semana)\b", 4.33),
    (r"\b(diario|daily|day|dia|día)\b", 21.0),
]

_CURRENCY_PATTERN = re.compile(
    r"(?:usd|us\$|\$|eur|€|r\$)\s*([0-9][0-9.,]*)\s*"
    r"(k|mil|thousand|mm|m|millon|millones|million|millions|milhao|milhoes)?",
    re.IGNORECASE,
)

_AMOUNT_THEN_CURRENCY_PATTERN = re.compile(
    r"([0-9][0-9.,]*)\s*"
    r"(k|mil|thousand|mm|m|millon|millones|million|millions|milhao|milhoes)?\s*"
    r"(?:usd|dolares|dólares|dollars|euros|reais)",
    re.IGNORECASE,
)

_HOURS_PATTERN = re.compile(
    r"([0-9][0-9.,]*)\s*(?:horas?|hours?|hrs?)\b",
    re.IGNORECASE,
)

# Hours are only treated as savings when the sentence expresses a reduction or
# release of effort, so durations such as "reducir el tiempo a 2 horas" are not
# misread as an economic benefit.
_SAVING_CONTEXT_PATTERN = re.compile(
    r"\b(ahorr\w*|ahorro|libera\w*|evita\w*|elimina\w*|save[sd]?|saving[s]?|freed?|avoid\w*|economiz\w*|poupa\w*)\b",
    re.IGNORECASE,
)

_PERCENT_PATTERN = re.compile(r"([0-9]{1,3}(?:[.,][0-9]+)?)\s*%")


def _normalize_number(raw: str) -> Optional[float]:
    """Parse a localized number string such as '1.250,50' or '1,250.50'."""
    text = raw.strip()
    if not text:
        return None

    has_comma = "," in text
    has_dot = "." in text
    if has_comma and has_dot:
        # The right-most separator is the decimal separator.
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif has_comma:
        # Comma is a decimal separator only when it is followed by 1-2 digits.
        if re.search(r",\d{1,2}$", text):
            text = text.replace(",", ".")
        else:
            text = text.replace(",", "")
    elif has_dot:
        if not re.search(r"\.\d{1,2}$", text):
            text = text.replace(".", "")

    try:
        return float(text)
    except ValueError:
        return None


def _period_factor(text: str) -> Tuple[float, str]:
    """Return the multiplier that converts the stated period into a month."""
    lowered = text.lower()
    for pattern, factor in _PERIOD_TO_MONTHLY:
        if re.search(pattern, lowered):
            if factor == 1.0:
                return factor, "monthly"
            if factor == 1.0 / 12.0:
                return factor, "annual"
            if factor == 1.0 / 3.0:
                return factor, "quarterly"
            if factor == 4.33:
                return factor, "weekly"
            return factor, "daily"
    # Without an explicit period, treat the figure as annual to stay conservative.
    return 1.0 / 12.0, "annual_assumed"


def _apply_multiplier(amount: float, multiplier: Optional[str]) -> float:
    if not multiplier:
        return amount
    return amount * _MULTIPLIER_WORDS.get(multiplier.lower(), 1)


def _extract_currency_amount(text: str) -> Optional[float]:
    candidates: List[float] = []
    for match in _CURRENCY_PATTERN.finditer(text):
        value = _normalize_number(match.group(1))
        if value is not None:
            candidates.append(_apply_multiplier(value, match.group(2)))
    for match in _AMOUNT_THEN_CURRENCY_PATTERN.finditer(text):
        value = _normalize_number(match.group(1))
        if value is not None:
            candidates.append(_apply_multiplier(value, match.group(2)))
    if not candidates:
        return None
    return max(candidates)


def _extract_hours(text: str) -> Optional[float]:
    candidates: List[float] = []
    for match in _HOURS_PATTERN.finditer(text):
        window = text[max(0, match.start() - 90): match.end() + 40]
        if not _SAVING_CONTEXT_PATTERN.search(window):
            continue
        value = _normalize_number(match.group(1))
        if value is not None:
            candidates.append(value)
    if not candidates:
        return None
    return max(candidates)


def _collect_value_text(idea: IdeaCase) -> str:
    parts = [idea.expected_value or "", idea.problem_statement or ""]
    if idea.business_validation is not None:
        parts.extend(idea.business_validation.score_breakdown or [])
        parts.extend(idea.business_validation.assumptions or [])
    if idea.clarification_interactions:
        for interaction in idea.clarification_interactions:
            for answer in interaction.answers or []:
                parts.append(getattr(answer, "answer", "") or "")
    return " \n ".join(part for part in parts if part)


def _estimate_monthly_savings(idea: IdeaCase) -> Tuple[float, str, str, List[str]]:
    """
    Return (monthly_savings_usd, basis, confidence, assumptions).

    Confidence is 'high' when a currency figure was stated, 'medium' when the
    value was expressed in saved hours, and 'low' when it was derived from the
    business value score because no quantitative signal was provided.
    """
    text = _collect_value_text(idea)
    assumptions: List[str] = []

    amount = _extract_currency_amount(text)
    if amount is not None and amount > 0:
        factor, period = _period_factor(text)
        monthly = amount * factor
        assumptions.append(f"Cifra declarada por el negocio: {amount:,.2f} USD ({period}).")
        if period == "annual_assumed":
            assumptions.append("No se indico periodicidad explicita; se asume valor anual (criterio conservador).")
        return round(monthly, 2), "stated_currency", "high", assumptions

    hours = _extract_hours(text)
    if hours is not None and hours > 0:
        factor, period = _period_factor(text)
        monthly_hours = hours * (factor if period != "annual_assumed" else 1.0)
        if period == "annual_assumed":
            assumptions.append("No se indico periodicidad explicita para las horas; se asume ahorro mensual.")
        monthly = monthly_hours * DEFAULT_HOURLY_COST_USD
        assumptions.append(f"Horas ahorradas detectadas: {hours:,.1f} ({period}).")
        assumptions.append(f"Costo hora cargado asumido: {DEFAULT_HOURLY_COST_USD:,.2f} USD.")
        return round(monthly, 2), "saved_hours", "medium", assumptions

    percent_match = _PERCENT_PATTERN.search(text)
    value_score = idea.business_validation.value_score if idea.business_validation else 0
    affected_users = max(1, len(idea.affected_users))
    monthly = affected_users * FALLBACK_VALUE_PER_USER_USD * (value_score / 100.0)
    assumptions.append(
        "El negocio no declaro un valor monetario; se deriva de usuarios afectados y score de valor."
    )
    assumptions.append(
        f"Base: {affected_users} usuarios x {FALLBACK_VALUE_PER_USER_USD:,.2f} USD x score {value_score}/100."
    )
    if percent_match:
        assumptions.append(
            f"Se detecto una mejora porcentual declarada ({percent_match.group(1)}%) sin base monetaria asociada."
        )
    return round(monthly, 2), "derived_from_value_score", "low", assumptions


def _resolve_monthly_cost(idea: IdeaCase) -> Tuple[float, str]:
    package = idea.architecture_package
    if package is not None and package.monthly_production_consumption is not None:
        return (
            float(package.monthly_production_consumption.estimated_monthly_cost_usd),
            "architecture_package",
        )
    return 0.0, "not_available"


def _build_verdict(ratio: Optional[float], confidence: str) -> Tuple[str, str]:
    if ratio is None:
        return (
            "insufficient_data",
            "No hay estimacion de consumo disponible. Genera el paquete de arquitectura antes de decidir.",
        )
    if confidence == "low":
        return (
            "needs_quantification",
            "El negocio no declaro un valor monetario verificable. Solicita la cifra de ahorro esperado "
            "antes de comparar contra el consumo estimado.",
        )
    if ratio >= RATIO_STRONG:
        return "favorable", "El valor esperado supera con holgura el consumo estimado."
    if ratio >= RATIO_ACCEPTABLE:
        return "acceptable", "El valor esperado cubre el consumo estimado con margen razonable."
    if ratio >= RATIO_BREAK_EVEN:
        return (
            "marginal",
            "El valor esperado apenas cubre el consumo estimado. Revisa alcance o arquitectura antes de funding.",
        )
    return (
        "unfavorable",
        "El consumo estimado supera el valor esperado. No se recomienda pasar a funding sin ajustes.",
    )


def build_value_economics(idea: IdeaCase) -> ValueEconomics:
    """Build the cost vs value comparison for an idea."""
    monthly_cost, cost_basis = _resolve_monthly_cost(idea)
    monthly_savings, value_basis, confidence, assumptions = _estimate_monthly_savings(idea)

    ratio: Optional[float] = None
    payback_months: Optional[float] = None
    if cost_basis != "not_available" and monthly_cost > 0:
        ratio = round(monthly_savings / monthly_cost, 2)
    elif cost_basis != "not_available" and monthly_cost == 0:
        ratio = None

    net_monthly = round(monthly_savings - monthly_cost, 2)
    if net_monthly > 0 and monthly_cost > 0:
        payback_months = round(monthly_cost / net_monthly, 2)

    verdict, message = _build_verdict(ratio, confidence)

    if cost_basis == "architecture_package":
        assumptions.append("Costo mensual tomado del paquete de arquitectura generado.")
    else:
        assumptions.append("Aun no existe estimacion de consumo del paquete de arquitectura.")

    return ValueEconomics(
        estimated_monthly_cost_usd=round(monthly_cost, 2),
        estimated_monthly_savings_usd=monthly_savings,
        net_monthly_value_usd=net_monthly,
        value_to_cost_ratio=ratio,
        payback_months=payback_months,
        value_basis=value_basis,
        value_confidence=confidence,
        cost_basis=cost_basis,
        verdict=verdict,
        message=message,
        assumptions=assumptions,
    )
