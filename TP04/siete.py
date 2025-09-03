from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Set, Dict, Tuple, Optional

"""
Backward chaining inference engine (encadenamiento hacia atrás) — MUY comentado en español.

Este script implementa un motor de inferencia proposicional de Horn (reglas del tipo
premisas_1 ∧ premisa_2 ∧ ... ∧ premisa_n  ->  conclusión) usando encadenamiento hacia atrás.

✔ Cómo funciona el encadenamiento hacia atrás
---------------------------------------------
Dado un objetivo (por ejemplo, 'a'), el motor intenta demostrarlo "yendo hacia atrás":
1) Si el objetivo ya es un hecho conocido, se da por demostrado.
2) Si no, busca reglas cuya conclusión sea el objetivo.
3) Para cada regla candidata, intenta demostrar *recursivamente* cada una de sus premisas.
4) Si todas las premisas de alguna regla se demuestran, entonces el objetivo queda demostrado.
5) Se evita el bucle con dos mecanismos: (a) una *pila de metas* (goals_stack) para detectar ciclos, 
   y (b) *memoización* de metas que ya fueron probadas como verdaderas o imposibles.

El algoritmo es correcto para bases de conocimiento con reglas de Horn, que es justamente el
formato del ejercicio 3 del TP (R1..R7).

Además del veredicto True/False, registramos un *árbol de prueba* para explicar QUÉ reglas
permitieron demostrar cada meta.
"""

# ---------------------------
#  Representación del Conocimiento
# ---------------------------

@dataclass(frozen=True)
class Rule:
    """
    Regla de Horn: premisas -> conclusión.
    
    - premises: conjunto de símbolos atómicos que deben ser verdaderos
    - head: símbolo atómico que se infiere si todas las premisas son verdaderas
    - name: etiqueta opcional para referenciar la regla en las explicaciones (p.ej., 'R1')
    """
    premises: Tuple[str, ...]
    head: str
    name: str = ""


@dataclass
class KnowledgeBase:
    """
    Base de conocimiento con:
      - facts: hechos atómicos ya conocidos como verdaderos (p.ej., {'d', 'e'})
      - rules: lista de reglas de Horn (Rule)
      
    También construimos un índice de acceso rápido para recuperar "reglas que concluyen X".
    """
    facts: Set[str] = field(default_factory=set)
    rules: List[Rule] = field(default_factory=list)
    _by_head: Dict[str, List[Rule]] = field(init=False, default_factory=dict)

    def __post_init__(self):
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        """Índice 'conclusión -> [reglas]' para acelerar el buscado de reglas candidatas."""
        self._by_head.clear()
        for r in self.rules:
            self._by_head.setdefault(r.head, []).append(r)

    def add_fact(self, f: str) -> None:
        self.facts.add(f)

    def add_rule(self, rule: Rule) -> None:
        self.rules.append(rule)
        self._by_head.setdefault(rule.head, []).append(rule)

    def rules_for(self, head: str) -> List[Rule]:
        """Devuelve todas las reglas cuya 'head' coincide con 'head'."""
        return self._by_head.get(head, [])


# ---------------------------
#  Estructuras para la explicación (árbol de prueba)
# ---------------------------

@dataclass
class ProofNode:
    """
    Nodo del árbol de prueba:
    - goal: meta demostrada en este nodo (ej., 'a')
    - rule: regla que permitió concluir esa meta (o None si fue un hecho base)
    - children: subpruebas para cada premisa de la regla
    """
    goal: str
    rule: Optional[Rule] = None
    children: List["ProofNode"] = field(default_factory=list)

    def pretty(self, level: int = 0) -> str:
        """Devuelve una representación legible del árbol de prueba."""
        indent = "  " * level
        if self.rule is None:
            return f"{indent}- {self.goal}  (hecho)"
        title = f"{indent}- {self.goal}  (por {self.rule.name or 'regla'})"
        subs = "\n".join(child.pretty(level + 1) for child in self.children)
        return f"{title}\n{subs}" if subs else title


# ---------------------------
#  Motor de encadenamiento hacia atrás
# ---------------------------

class BackwardChainer:
    """
    Motor básico de encadenamiento hacia atrás para reglas de Horn.
    
    Soporta:
    - Memoización de éxitos y fracasos para eficiencia.
    - Detección de ciclos con una pila de metas.
    - Generación de árbol de prueba inteligible.
    """
    def __init__(self, kb: KnowledgeBase):
        self.kb = kb
        # Cache de metas ya resueltas: símbolo -> (éxito, ProofNode opcional)
        self._cache_success: Dict[str, ProofNode] = {}
        self._cache_failure: Set[str] = set()

    def prove(self, goal: str) -> Tuple[bool, Optional[ProofNode]]:
        """
        Intenta demostrar 'goal'. Devuelve (True, prueba) si lo logra, o (False, None) si no.
        """
        # Usamos una pila para detectar ciclos (ej.: a depende de b, b de a).
        stack: List[str] = []
        success, node = self._prove_recursive(goal, stack)
        return success, node

    def _prove_recursive(self, goal: str, stack: List[str]) -> Tuple[bool, Optional[ProofNode]]:
        # 1) Ya lo conocés como hecho
        if goal in self.kb.facts:
            return True, ProofNode(goal=goal, rule=None, children=[])

        # 2) Evitar bucles: si la meta ya está en la pila, hay dependencia circular
        if goal in stack:
            return False, None

        # 3) Reutilizar resultados previos si existen
        if goal in self._cache_success:
            return True, self._cache_success[goal]
        if goal in self._cache_failure:
            return False, None

        # 4) Buscar reglas que concluyan 'goal'
        rules = self.kb.rules_for(goal)
        if not rules:
            # No hay manera de probar esta meta con reglas: fracaso
            self._cache_failure.add(goal)
            return False, None

        # 5) Intentar cada regla candidata en orden (DFS)
        stack.append(goal)  # Push para detección de ciclo en sub-ramas
        try:
            for rule in rules:
                # Intentar demostrar todas las premisas de esta regla
                children: List[ProofNode] = []
                all_premises_ok = True
                for prem in rule.premises:
                    ok, child = self._prove_recursive(prem, stack)
                    if not ok:
                        all_premises_ok = False
                        break
                    assert child is not None
                    children.append(child)

                if all_premises_ok:
                    # ¡Éxito! Construimos el nodo de prueba y lo memorizamos
                    node = ProofNode(goal=goal, rule=rule, children=children)
                    self._cache_success[goal] = node
                    # Nota: no añadimos goal a los hechos para mantener la explicación separada de los datos
                    return True, node

            # Ninguna regla logró demostrar el objetivo
            self._cache_failure.add(goal)
            return False, None
        finally:
            stack.pop()  # Pop al volver de la rama actual


# ---------------------------
#  Utilidades de ayuda
# ---------------------------

def build_kb_from_ex3() -> KnowledgeBase:
    """
    Construye la base de conocimiento EXACTA del Ejercicio 3 del TP:

    R1: b ∧ c → a
    R2: d ∧ e → b
    R3: g ∧ e → b
    R4: e → c
    R5: d
    R6: e
    R7: a ∧ g → f
    """
    kb = KnowledgeBase()
    # Hechos (R5 y R6 son reglas unitarias, las tomamos como hechos)
    kb.add_fact("d")
    kb.add_fact("e")

    # Reglas no unitarias
    kb.add_rule(Rule(premises=("b", "c"), head="a", name="R1"))
    kb.add_rule(Rule(premises=("d", "e"), head="b", name="R2"))
    kb.add_rule(Rule(premises=("g", "e"), head="b", name="R3"))
    kb.add_rule(Rule(premises=("e",), head="c", name="R4"))  # también podría modelarse como hecho si e es hecho
    kb.add_rule(Rule(premises=("a", "g"), head="f", name="R7"))
    return kb


def demo():
    """
    Demostración breve:
    - Intenta probar 'a' (debería ser True).
    - Intenta probar 'f' (debería fallar porque 'g' no se puede probar).
    Imprime los árboles de prueba cuando existan.
    """
    kb = build_kb_from_ex3()
    engine = BackwardChainer(kb)

    print("=== Prueba de 'a' ===")
    ok_a, proof_a = engine.prove("a")
    print("Resultado:", ok_a)
    if ok_a and proof_a:
        print(proof_a.pretty())

    print("\n=== Prueba de 'f' ===")
    ok_f, proof_f = engine.prove("f")
    print("Resultado:", ok_f)
    if ok_f and proof_f:
        print(proof_f.pretty())
    else:
        print("No se pudo demostrar 'f' porque falta 'g'.")

if __name__ == "__main__":
    demo()
