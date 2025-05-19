# Ingreso y separación de las reglas de la gramática

# Ingreso y separación de las reglas de la gramática
def parse_grammar_input():
    n = int(input("Ingrese el número de no terminales: "))
    productions = {}
    nonterminals = []

    print("Ingrese las producciones una por línea con el formato: NT -> alpha | beta")
    print("IMPORTANTE: Separar cada No-Terminal o Terminal por un espacio y cada Producción por un salto de línea\n")
    print("Reglas de Producción:")
    for _ in range(n):
        line = input().strip()
        if not line:
            continue
        head, bodies = line.split("->")
        head = head.strip()
        nonterminals.append(head)
        alternatives = [alt.strip().split() for alt in bodies.strip().split("|")]
        productions[head] = alternatives

    return productions, nonterminals


# Cálculo de FIRST

def compute_first(productions, nonterminals):
    first = {nt: set() for nt in nonterminals}

    def first_of(symbol):
        if symbol not in nonterminals:
            return {symbol}
        return first[symbol]

    changed = True
    while changed:
        changed = False
        for nt in nonterminals:
            for production in productions[nt]:
                i = 0
                while i < len(production):
                    sym_first = first_of(production[i])
                    before = len(first[nt])
                    first[nt].update(sym_first - {'e'})
                    if 'e' not in sym_first:
                        break
                    i += 1
                else:
                    first[nt].add('e')
                if len(first[nt]) > before:
                    changed = True

    return first


# Cálculo de FOLLOW

def compute_follow(productions, nonterminals, first, start_symbol):
    follow = {nt: set() for nt in nonterminals}
    follow[start_symbol].add('$')

    def first_of_sequence(seq):
        result = set()
        for symbol in seq:
            symbol_first = first[symbol] if symbol in first else {symbol}
            result.update(symbol_first - {'e'})
            if 'e' not in symbol_first:
                break
        else:
            result.add('e')
        return result

    changed = True
    while changed:
        changed = False
        for A in nonterminals:
            for production in productions[A]:
                for i in range(len(production)):
                    B = production[i]
                    if B in nonterminals:
                        beta = production[i+1:]

                        # Caso 1: FOLLOW(B) ← FIRST(beta) \ {ε}
                        first_beta = first_of_sequence(beta)
                        before = len(follow[B])
                        follow[B].update(first_beta - {'e'})

                        # Caso 2: si beta == ε o FIRST(beta) contiene ε, FOLLOW(B) ← FOLLOW(A)
                        if not beta or 'e' in first_beta:
                            follow[B].update(follow[A])

                        if len(follow[B]) > before:
                            changed = True

    return follow

def construct_ll1_table(productions, nonterminals, first, follow):
    table = {nt: {} for nt in nonterminals}

    for A in nonterminals:
        for production in productions[A]:
            first_alpha = set()
            i = 0
            while i < len(production):
                sym = production[i]
                if sym in nonterminals:
                    sym_first = first[sym]
                    first_alpha.update(sym_first - {'e'})
                    if 'e' in sym_first:
                        i += 1
                    else:
                        break
                else:
                    first_alpha.add(sym)
                    break
            else:
                first_alpha.add('e')

            for terminal in first_alpha:
                if terminal != 'e':
                    table[A][terminal] = ' '.join(production)

            if 'e' in first_alpha:
                for terminal in follow[A]:
                    table[A][terminal] = 'e'

    return table

def is_ll1_grammar(ll1_table):
    for nt in ll1_table:
        seen = set()
        for terminal in ll1_table[nt]:
            if terminal in seen:
                return False
            seen.add(terminal)
    return True

def parse_ll1(input_string, productions, ll1_table, start_symbol):
    stack = [ '$', start_symbol ]
    tokens = input_string.strip().split() + ['$']
    index = 0

    while stack:
        top = stack.pop()
        current_token = tokens[index]

        if top == 'e':
            continue
        elif top == current_token:
            index += 1
        elif top in productions:  # Es un no terminal
            rule = ll1_table[top].get(current_token)
            if not rule:
                return False
            symbols = rule.split()[::-1] if rule != 'e' else []
            stack.extend(symbols)
        else:
            return False

    return index == len(tokens)
# Funciones auxiliares para SLR(1)
def augment_grammar(productions, start_symbol):
    new_start = start_symbol + "'"
    augmented = {new_start: [(start_symbol,)]}
    for head, bodies in productions.items():
        augmented[head] = bodies
    return augmented, new_start

def closure(items, productions):
    closure_set = set(items)
    changed = True
    while changed:
        changed = False
        new_items = set()
        for head, body in closure_set:
            if '.' in body:
                dot_pos = body.index('.')
                if dot_pos + 1 < len(body):
                    B = body[dot_pos + 1]
                    if B in productions:
                        for prod in productions[B]:
                            item = (B, ('.',) + tuple(prod))
                            if item not in closure_set:
                                new_items.add(item)
        if new_items:
            closure_set.update(new_items)
            changed = True
    return closure_set

def goto(items, symbol, productions):
    next_items = set()
    for head, body in items:
        for i in range(len(body) - 1):
            if body[i] == '.' and body[i + 1] == symbol:
                new_body = body[:i] + (symbol, '.') + body[i + 2:]
                next_items.add((head, new_body))
    return closure(next_items, productions)

def build_lr0_automaton(productions, start_symbol):
    initial_item = (start_symbol, ('.',) + tuple(productions[start_symbol][0]))
    initial_closure = closure({initial_item}, productions)
    states = [initial_closure]
    transitions = {}

    while True:
        new_states = []
        for i, state in enumerate(states):
            symbols = set(s for head, body in state for s in body if s != '.')
            for symbol in symbols:
                target = goto(state, symbol, productions)
                if target and target not in states and target not in new_states:
                    new_states.append(target)
                if target:
                    j = states.index(target) if target in states else len(states) + new_states.index(target)
                    transitions[(i, symbol)] = j
        if not new_states:
            break
        states.extend(new_states)

    return states, transitions

def construct_slr1_table(states, transitions, productions, follow, start_symbol):
    slr_table = [{} for _ in states]

    for i, state in enumerate(states):
        for item in state:
            head, body = item
            if body[-1] == '.':
                if head == start_symbol:
                    slr_table[i]['$'] = 'accept'
                else:
                    for a in follow[head]:
                        slr_table[i][a] = f'reduce {head} -> {" ".join(body[:-1])}'
            else:
                dot_pos = body.index('.')
                if dot_pos + 1 < len(body):
                    symbol = body[dot_pos + 1]
                    if (i, symbol) in transitions:
                        action = 'shift' if symbol not in productions else ''
                        slr_table[i][symbol] = f'{action} {transitions[(i, symbol)]}'

    return slr_table

def parse_slr1(input_string, slr_table, productions, start_symbol):
    stack = [0]
    tokens = input_string.strip().split() + ['$']
    index = 0

    while True:
        state = stack[-1]
        token = tokens[index]
        action = slr_table[state].get(token)

        if not action:
            return False
        elif action == 'accept':
            return True
        elif action.startswith('shift'):
            _, next_state = action.split()
            stack.append(token)
            stack.append(int(next_state))
            index += 1
        elif action.startswith('reduce'):
            _, rule = action.split(' ', 1)
            head, body = rule.split('->')
            head = head.strip()
            body = body.strip().split()
            if body != ['e']:
                for _ in range(len(body) * 2):
                    stack.pop()
            state = stack[-1]
            stack.append(head)
            goto_state = slr_table[state].get(head)
            if not goto_state:
                return False
            stack.append(int(goto_state))

if __name__ == '__main__':
    productions, nonterminals = parse_grammar_input()
    start_symbol = nonterminals[0]

    first = compute_first(productions, nonterminals)
    follow = compute_follow(productions, nonterminals, first, start_symbol)

    print("\nConjuntos FIRST:")
    for nt in first:
        print(f"FIRST({nt}) = {{ {', '.join(first[nt])} }}")

    print("\nConjuntos FOLLOW:")
    for nt in follow:
        print(f"FOLLOW({nt}) = {{ {', '.join(follow[nt])} }}")

    ll1_table = construct_ll1_table(productions, nonterminals, first, follow)
    print("\nTabla LL(1):")
    terminals = sorted({t for row in ll1_table.values() for t in row})
    print("NT".ljust(10), *(t.ljust(15) for t in terminals))
    for nt in nonterminals:
        print(nt.ljust(10), *(ll1_table[nt].get(t, '').ljust(15) for t in terminals))

    if is_ll1_grammar(ll1_table):
        print("\nLa gramática es LL(1). Ingrese cadenas (vacía para terminar):")
        while True:
            cadena = input("Cadena: ").strip()
            if cadena == "":
                break
            print("yes" if parse_ll1(cadena, productions, ll1_table, start_symbol) else "no")
    else:
        print("\nLa gramática NO es LL(1).")

    # SLR(1) Analysis
    augmented_productions, new_start = augment_grammar(productions, start_symbol)
    states, transitions = build_lr0_automaton(augmented_productions, new_start)
    slr_table = construct_slr1_table(states, transitions, augmented_productions, follow, new_start)

    print("\nTabla SLR(1):")
    all_terminals = sorted(set().union(*[set(row.keys()) for row in slr_table]))
    print("Estado".ljust(10), *(t.ljust(20) for t in all_terminals))
    for i, row in enumerate(slr_table):
        print(str(i).ljust(10), *(row.get(t, '').ljust(20) for t in all_terminals))

    print("\nVerificación con SLR(1). Ingrese cadenas (vacía para terminar):")
    while True:
        cadena = input("Cadena: ").strip()
        if cadena == "":
            break
        print("yes" if parse_slr1(cadena, slr_table, productions, start_symbol) else "no")
