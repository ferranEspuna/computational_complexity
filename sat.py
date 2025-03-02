from dataclasses import dataclass
from networkx import DiGraph
import matplotlib.pyplot as plt
from pyvis.network import Network


@dataclass(frozen=True)
class Literal:
    name: str
    positive: bool = True

    def __str__(self):
        return ('' if self.positive else '¬') + self.name

    def __invert__(self):
        return Literal(self.name, not self.positive)

    def __or__(self, other):

        if type(other) is Literal:
            return Clause.from_literals((self, other))

        else:
            return other | self


def TRUE():
    return Clause(true=True)


def FALSE():
    return Clause()


@dataclass(frozen=True)
class Clause:
    literals: tuple[Literal, ...] = ()
    true: bool = False

    def add(self, literal: Literal):
        # If this clause is TRUE(), we don't need to add any more literals
        if self.true:
            return self

        # If literals is None (empty clause), initialize as an empty tuple
        for l in self.literals:
            if l.name == literal.name:
                if l.positive == literal.positive:
                    return self
                else:
                    return TRUE()

        # Create a new clause with the new literal added
        return Clause.from_literals(self.literals + (literal,))

    def __or__(self, other):

        if type(other) is Literal:
            return self.add(other)

        if self.true or other.true:
            return TRUE()
        # Merge literals properly while ensuring no duplicates
        return Clause.from_literals(self.literals + other.literals)

    def __str__(self):
        if self.true:
            return 'TRUE'
        return '(' + ' ∨ '.join(str(l) for l in self.literals) + ')'

    @classmethod
    def from_literals(cls, literals):
        # Ensure no duplicates and properly combine literals
        unique_literals = []
        for literal in literals:
            if literal not in unique_literals:
                unique_literals.append(literal)
        # Return a new Clause instance with unique literals
        return cls(literals=tuple(unique_literals))

    def __evaluate__(self, **assignment):
        if self.true:
            return TRUE()

        new_literals = []
        for literal in self.literals:
            if literal.name in assignment:
                if assignment[literal.name] == literal.positive:
                    return TRUE()
            else:
                new_literals.append(literal)

        return Clause.from_literals(new_literals)


def make_digraph(clauses, assignments):
    graph = DiGraph()

    all_possible_literals = set()
    for clause in clauses:
        for literal in clause.literals:
            all_possible_literals.add(literal)
            all_possible_literals.add(~literal)

    literals = list(all_possible_literals)

    label_sizes = []

    for lit in literals:
        graph.add_node(str(lit), shape='box')
        if lit.name in assignments:
            if assignments[lit.name] == lit.positive:
                graph.add_node(str(lit), shape='box', color='lightgreen')
            else:
                graph.add_node(str(lit), shape='box', color='pink')
        label_sizes.append(300)

    for c in clauses:
        graph.add_node(str(c), shape='box')
        label_sizes.append(60 * len(str(c)) ** 2)

    for c in clauses:
        for l in c.literals:
            graph.add_edge(str(l), str(c))

    for lit in literals:
        graph.add_edge(str(lit), str(~lit))

    return graph, label_sizes


if __name__ == '__main__':
    x = Literal('x')
    y = Literal('y')
    z = Literal('z')
    t = Literal('t')

    c1 = x | y | z
    c2 = ~x | z | t
    c3 = ~y | ~z | ~t
    c4 = ~x | ~y | t

    clauses = [c1, c2, c3, c4]

    assignments = {
        'x': True,
        'y': False,
        'z': True,
        't': False
    }

    for c in clauses:
        print(c.__evaluate__(**assignments))



    # plot the graph
    graph, sizes = make_digraph(clauses, assignments)

    net = Network(
        directed=True,
        select_menu=True,  # Show part 1 in the plot (optional)
        filter_menu=True,  # Show part 2 in the plot (optional)
    )
    net.show_buttons()  # Show part 3 in the plot (optional)
    net.from_nx(graph)  # Create directly from nx graph
    net.show('test.html', notebook=False)


    plt.show()
