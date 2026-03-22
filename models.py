"""
models.py — Status definitions, constants, and helpers.
Pure data — no Streamlit imports, no side effects.
"""

STATUS_CONFIG = {
    'proposta_enviada': {'label': 'Proposta',      'color': '#6B7280', 'order': 1},
    'em_andamento':     {'label': 'Em Andamento',  'color': '#3B82F6', 'order': 2},
    'concluido':        {'label': 'Concluído',     'color': '#059669', 'order': 3},
    'perdido':          {'label': 'Perdido',       'color': '#EF4444', 'order': 4},
}

# Map old statuses to new simplified ones for backward compatibility
_STATUS_MIGRATION = {
    'em_negociacao':     'em_andamento',
    'aprovado':          'em_andamento',
    'contrato_assinado': 'em_andamento',
    'em_execucao':       'em_andamento',
}

STATUS_LABELS = [v['label'] for v in sorted(STATUS_CONFIG.values(), key=lambda x: x['order'])]
STATUS_KEYS   = [k for k in sorted(STATUS_CONFIG, key=lambda x: STATUS_CONFIG[x]['order'])]


def _migrate_status(key: str) -> str:
    """Map old status keys to current simplified keys."""
    return _STATUS_MIGRATION.get(key, key)


def status_key_to_label(key: str) -> str:
    key = _migrate_status(key)
    return STATUS_CONFIG.get(key, {}).get('label', key)


def status_label_to_key(label: str) -> str:
    for k, v in STATUS_CONFIG.items():
        if v['label'] == label:
            return k
    return 'proposta_enviada'


def status_dot(key: str) -> str:
    key = _migrate_status(key)
    color = STATUS_CONFIG.get(key, {}).get('color', '#6B7280')
    return (
        f"<span style='display:inline-block;width:10px;height:10px;"
        f"border-radius:50%;background:{color};margin-right:6px;'></span>"
    )


def status_dot_text(key: str) -> str:
    key = _migrate_status(key)
    return f"● {STATUS_CONFIG.get(key, {}).get('label', key)}"
