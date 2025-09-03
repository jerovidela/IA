"""
Motor de inferencia por contradicción (resolución proposicional).

Idea principal
--------------
Un conjunto de proposiciones (en CNF) es **inconsistente** si, aplicando
la **regla de resolución** entre sus cláusulas, se puede derivar la
**cláusula vacía** (∅). La cláusula vacía representa una contradicción.

Representación
--------------
- Cada **literal** es una tupla (símbolo:str, es_negada:bool), por ejemplo: ('a', False) = a, ('a', True) = ¬a.
- Cada **cláusula** es un `frozenset` de literales (disyunción de literales).
- Una **CNF** es un `set` de cláusulas (conjunción de cláusulas).

Regla de resolución
-------------------
Dadas dos cláusulas C1 y C2, y un símbolo p, si en C1 está p y en C2 está ¬p
(entonces “chocan” en p), el resolvente es:
    resolvente = (C1 - {p}) ∪ (C2 - {¬p})
Si en algún momento obtenemos el conjunto vacío, se detectó una contradicción.

Este archivo incluye además la traducción a CNF de las reglas del Ejercicio 3:
R1: b ∧ c → a        -> (¬b ∨ ¬c ∨ a)
R2: d ∧ e → b        -> (¬d ∨ ¬e ∨ b)
R3: g ∧ e → b        -> (¬g ∨ ¬e ∨ b)
R4: e → c            -> (¬e ∨ c)
R5: d                -> (d)
R6: e                -> (e)
R7: a ∧ g → f        -> (¬a ∨ ¬g ∨ f)

Como solo queremos chequear **inconsistencia del conjunto**, NO añadimos
la negación de ninguna consulta. Si la CNF por sí sola deriva ∅, es inconsistente.
"""
from __future__ import annotations
from typing import Set, FrozenSet, Tuple, Iterable

Literal = Tuple[str, bool]   # (symbol, is_negated) ; is_negated=True representa ¬symbol
Clause  = FrozenSet[Literal] # disyunción de literales
CNF     = Set[Clause]        # conjunción de cláusulas


# ---------------------------
# Utilidades sobre literales
# ---------------------------

def neg(lit: Literal) -> Literal:
    """Negación de un literal: (p, False) -> (p, True) y viceversa."""
    return (lit[0], not lit[1])

def has_complement(c1: Clause, c2: Clause) -> Iterable[Tuple[Literal, Literal]]:
    """
    Devuelve pares (l, ¬l) tales que l ∈ c1 y ¬l ∈ c2.
    Sirve para saber en qué literales se pueden resolver C1 y C2.
    """
    s2 = set(c2)
    for l in c1:
        comp = neg(l)
        if comp in s2:
            yield (l, comp)

def clause_to_str(c: Clause) -> str:
    """Imprime una cláusula de forma legible, p. ej. (¬b ∨ ¬c ∨ a) o (⊥) si es vacía."""
    if not c:
        return "⊥"  # cláusula vacía (contradicción)
    lits = []
    for sym, is_neg in sorted(c, key=lambda x: (x[0], x[1])):
        lits.append(("¬" if is_neg else "") + sym)
    return "(" + " ∨ ".join(lits) + ")"

def cnf_to_str(F: CNF) -> str:
    """Imprime una CNF (conjunción de cláusulas)."""
    if not F:
        return "VERDAD (CNF vacía)"
    return " ∧ ".join(sorted([clause_to_str(c) for c in F]))


# ---------------------------
# Resolución proposicional
# ---------------------------

def resolve(c1: Clause, c2: Clause) -> Set[Clause]:
    """
    Aplica resolución entre C1 y C2. Devuelve el conjunto de resolventes posibles 
    (podría haber más de uno si hay varios literales complementarios).
    Si se obtiene la cláusula vacía, se incluirá como `frozenset()` en el resultado.
    """
    resolvents: Set[Clause] = set()
    for l, nl in has_complement(c1, c2):
        new_clause = frozenset((c1 - {l}) | (c2 - {nl}))
        # Simplificaciones básicas: quitar literales repetidos y detectar tautologías p ∨ ¬p
        if any((sym, True) in new_clause and (sym, False) in new_clause for sym, _ in new_clause):
            # Es una tautología -> no aporta nada, se puede ignorar
            continue
        resolvents.add(new_clause)
    return resolvents

def resolution_refutation(F: CNF, verbose: bool = True) -> bool:
    """
    Intenta derivar la cláusula vacía por resolución a partir de F.
    Devuelve True si se encuentra ⊥ (inconsistencia), False si no (hasta saturar).

    Estrategia: algoritmo de resolución por saturación clásico (pairwise).
    """
    # Trabajamos con una copia para no modificar el original
    clauses: Set[Clause] = set(F)
    new: Set[Clause] = set()

    if verbose:
        print("CNF inicial:")
        for c in clauses:
            print("  ", clause_to_str(c))

    # Bucle de saturación: intentar todas las resoluciones posibles
    while True:
        pairs = []
        cls_list = list(clauses)
        n = len(cls_list)
        for i in range(n):
            for j in range(i + 1, n):
                pairs.append((cls_list[i], cls_list[j]))

        generated_any = False
        for (c1, c2) in pairs:
            resolvents = resolve(c1, c2)
            for r in resolvents:
                if not r:
                    if verbose:
                        print("\nSe derivó la cláusula vacía por resolución de:")
                        print("   ", clause_to_str(c1))
                        print("   ", clause_to_str(c2))
                        print("=>  ⊥  (INCONSISTENTE)")
                    return True  # inconsistente
                if r not in clauses and r not in new:
                    new.add(r)
                    generated_any = True
                    if verbose:
                        print("Nuevo resolvente:", clause_to_str(r))

        if not generated_any:
            # No se generaron más cláusulas -> saturado sin llegar a ⊥
            if verbose:
                print("\nSaturado sin contradicción. No se pudo derivar ⊥.")
            return False
        clauses |= new
        new.clear()


# ---------------------------
# Construir la CNF del Ejercicio 3
# ---------------------------

def lit(p: str, negado: bool = False) -> Literal:
    return (p, negado)

def cnf_from_ex3() -> CNF:
    """
    Traducción directa de las reglas y hechos del Ejercicio 3 a CNF:
      (¬b ∨ ¬c ∨ a), (¬d ∨ ¬e ∨ b), (¬g ∨ ¬e ∨ b), (¬e ∨ c), (d), (e), (¬a ∨ ¬g ∨ f)
    """
    F: CNF = set()
    # R1: b ∧ c → a     ==> (¬b ∨ ¬c ∨ a)
    F.add(frozenset({lit('b', True), lit('c', True), lit('a', False)}))
    # R2: d ∧ e → b     ==> (¬d ∨ ¬e ∨ b)
    F.add(frozenset({lit('d', True), lit('e', True), lit('b', False)}))
    # R3: g ∧ e → b     ==> (¬g ∨ ¬e ∨ b)
    F.add(frozenset({lit('g', True), lit('e', True), lit('b', False)}))
    # R4: e → c         ==> (¬e ∨ c)
    F.add(frozenset({lit('e', True), lit('c', False)}))
    # R5: d             ==> (d)
    F.add(frozenset({lit('d', False)}))
    # R6: e             ==> (e)
    F.add(frozenset({lit('e', False)}))
    # R7: a ∧ g → f     ==> (¬a ∨ ¬g ∨ f)
    F.add(frozenset({lit('a', True), lit('g', True), lit('f', False)}))
    return F


# ---------------------------
# Demostración con el Ejercicio 3
# ---------------------------

def demo():
    print("=== Chequeo de inconsistencia por resolución (Ejercicio 3) ===\n")
    F = cnf_from_ex3()
    inconsistente = resolution_refutation(F, verbose=True)
    print("\n¿La base es inconsistente?", inconsistente)
    if not inconsistente:
        print("Interpretación: las reglas + hechos NO implican contradicción lógica.")

if __name__ == "__main__":
    demo()
