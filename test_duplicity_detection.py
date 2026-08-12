#!/usr/bin/env python
"""Test del algoritmo mejorado de detección de duplicidad"""

from api.app.matching_service import (
    _calculate_keyword_similarity,
    _calculate_string_similarity,
    _calculate_concept_overlap,
    _normalize_text_for_semantic_comparison,
    _apply_semantic_synonyms,
)

# Test casos de uso reales
test_cases = [
    {
        "name": "Predicción vs Predictor",
        "text1": "Prediccion de Rotacion de Clientes Premium",
        "text2": "Sistema Predictor de Rotacion de Clientes Premium"
    },
    {
        "name": "Con descripción reducida",
        "text1": "Prediccion de Rotacion de Clientes Premium - Análisis predictivo",
        "text2": "Sistema Predictor de Rotacion de Clientes Premium"
    },
    {
        "name": "Distinto wording, mismo objetivo",
        "text1": "Detección de fraude en transacciones",
        "text2": "Sistema de identificación de transacciones fraudulentas"
    }
]

print("\n" + "="*80)
print("TEST: Análisis de Duplicidad Semántica Mejorado")
print("="*80)

for test in test_cases:
    print(f"\n📋 {test['name']}")
    print(f"   Texto 1: {test['text1']}")
    print(f"   Texto 2: {test['text2']}")
    
    # Similitud de keywords
    kw_sim = _calculate_keyword_similarity(test['text1'], test['text2'])
    
    # Similitud estructural
    str_sim = _calculate_string_similarity(test['text1'], test['text2'])
    
    # Solapamiento conceptual
    concept_sim = _calculate_concept_overlap(test['text1'], test['text2'])
    
    # Normalización
    norm1 = _normalize_text_for_semantic_comparison(test['text1'])
    norm2 = _normalize_text_for_semantic_comparison(test['text2'])
    
    # Sinónimos
    syn1 = _apply_semantic_synonyms(test['text1'])
    syn2 = _apply_semantic_synonyms(test['text2'])
    
    print(f"\n   Resultados:")
    print(f"   - Keywords Similarity:   {kw_sim:6.2f}%")
    print(f"   - String Similarity:     {str_sim:6.2f}%")
    print(f"   - Concept Overlap:       {concept_sim:6.2f}%")
    print(f"   - Max Score:             {max(kw_sim, str_sim, concept_sim):6.2f}%")
    
    print(f"\n   Análisis Semántico:")
    print(f"   - Normalizado 1: {norm1}")
    print(f"   - Normalizado 2: {norm2}")
    print(f"   - Conceptos en 1: {syn1}")
    print(f"   - Conceptos en 2: {syn2}")
    
    is_duplicate = concept_sim > 60 or max(kw_sim, str_sim) > 50
    print(f"\n   ⚠️  DETECTA DUPLICIDAD: {'✓ SÍ' if is_duplicate else '✗ NO'}")

print("\n" + "="*80)
print("✓ Tests completados")
print("="*80)
