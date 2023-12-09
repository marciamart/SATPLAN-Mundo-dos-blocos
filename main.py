import sys
from pysat.solvers import Glucose4
from instance_manager.satplan_instance import SatPlanInstance, SatPlanInstanceMapper

def create_literal_for_level(level, literal):
    pure_atom = literal.replace("~","")
    return f"~{level}_{pure_atom}" if literal[0] == "~" else f"{level}_{pure_atom}"

def create_literals_for_level_from_list(level, literals): #criando ações para cada nivel e cada literal
    return [create_literal_for_level(level, literal) for literal in literals]

def create_state_from_true_atoms(true_atoms, all_atoms):
    initial_state = [f"~{atom}" for atom in all_atoms if atom not in true_atoms]
    return true_atoms + initial_state

def create_state_from_literals(literals, all_atoms):
    positive_literals = [literal for literal in literals if literal[0] != "~"]
    return create_state_from_true_atoms(positive_literals, all_atoms)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python your_script.py <filename>")
        sys.exit(1)       

    satPlanInstance = SatPlanInstance(sys.argv[1])
    instanceMapper  = SatPlanInstanceMapper()
    formula = Glucose4()

    nivel = 1
    status = False

    #estado inicial 
    estado_inicial = create_literals_for_level_from_list(nivel, create_state_from_literals(satPlanInstance.get_initial_state(), satPlanInstance.get_state_atoms()))
    instanceMapper.add_list_of_literals_to_mapping(estado_inicial)
    for states in estado_inicial:
            formula.add_clause([instanceMapper.get_literal_from_mapping(states)])
            print(instanceMapper.get_literal_from_mapping(states))       

    print(instanceMapper.mapping)
    while status == False:
        print('////////////////////////////////ESTOU AQUI////////////////////////////////')

        # estado final
        estado_final = create_literals_for_level_from_list(nivel+1,satPlanInstance.get_final_state())
        instanceMapper.add_list_of_literals_to_mapping(estado_final)
        for states in estado_final:
            formula.add_clause([instanceMapper.get_literal_from_mapping(states)])
            print(instanceMapper.get_literal_from_mapping(states))

        #acoes de cada nivel a serem escolhidas por vez
        clausula = []
        acoes = create_literals_for_level_from_list(nivel,satPlanInstance.get_actions())
        instanceMapper.add_list_of_literals_to_mapping(acoes)
        #tem que ser uma delas
        for acao in acoes:
            clausula.append(instanceMapper.get_literal_from_mapping(acao))
        formula.add_clause(clausula)
        print(clausula)
        #mas so uma delas
        for acao in acoes:
            clausula.clear()
            clausula.append(instanceMapper.get_literal_from_mapping(acao))
            for a in acoes:
                if a != acao:
                    clausula.append(-instanceMapper.get_literal_from_mapping(a))
            formula.add_clause(clausula)
            print(clausula)
            
        # criando literais para o proximo nivel
        nestado = create_literals_for_level_from_list(nivel+1, satPlanInstance.get_state_atoms() + satPlanInstance.get_actions())
        instanceMapper.add_list_of_literals_to_mapping(nestado)
        print(instanceMapper.mapping)

        print(instanceMapper.mapping)
        for acao in satPlanInstance.get_actions():
            for pre in satPlanInstance.get_action_preconditions(acao):
                formula.add_clause([-instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), instanceMapper.get_literal_from_mapping(f'{nivel}_{pre}')])
                print(-instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), instanceMapper.get_literal_from_mapping(f'{nivel}_{pre}'))
        print('//////////////////////')
        print(instanceMapper.mapping)
        for acao in satPlanInstance.get_actions():
            for pos in satPlanInstance.get_action_posconditions(acao):
                if pos[0] == '~':
                    pos = pos.replace("~","")
                    formula.add_clause([-instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), -instanceMapper.get_literal_from_mapping(f'{nivel+1}_{pos}')])
                    print(-instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), -instanceMapper.get_literal_from_mapping(f'{nivel+1}_{pos}'))
                else: 
                    formula.add_clause([-instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), instanceMapper.get_literal_from_mapping(f'{nivel+1}_{pos}')])
                    print(-instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), instanceMapper.get_literal_from_mapping(f'{nivel+1}_{pos}'))
            afetados = [i for i in satPlanInstance.get_state_atoms() if i not in pos]
            for afetado in afetados:
                formula.add_clause([-instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), -instanceMapper.get_literal_from_mapping(f'{nivel}_{afetado}'), instanceMapper.get_literal_from_mapping(f'{nivel+1}_{acao}') ])
                formula.add_clause([instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), -instanceMapper.get_literal_from_mapping(f'{nivel}_{afetado}'), instanceMapper.get_literal_from_mapping(f'{nivel+1}_{acao}') ])
        
        for acao in satPlanInstance.get_actions():
          for acao1 in satPlanInstance.get_actions():
              formula.add_clause([-instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), -instanceMapper.get_literal_from_mapping(f'{nivel}_{acao1}')])

        nivel += 1
        if formula.solve():
            print(formula.get_model())
            status = True

        if nivel == 5 :
            status = True