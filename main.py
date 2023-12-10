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


    niveis = 1
    
    niveln = create_literals_for_level_from_list(0, satPlanInstance.get_atoms())
    instanceMapper.add_list_of_literals_to_mapping(niveln)


    while True:
        formula = Glucose4()

        #criar todos os literais do proximo nivel
        niveln = create_literals_for_level_from_list(niveis, satPlanInstance.get_atoms())
        instanceMapper.add_list_of_literals_to_mapping(niveln)

        niveln = create_literals_for_level_from_list(niveis+1, satPlanInstance.get_atoms())
        instanceMapper.add_list_of_literals_to_mapping(niveln)

        # estado inical
        for states in create_state_from_literals(satPlanInstance.get_initial_state(),satPlanInstance.get_state_atoms()):
                if states[0] == '~':
                    states = states.replace("~","")
                    formula.add_clause([-instanceMapper.get_literal_from_mapping(f'{0}_{states}')])
                else: 
                    formula.add_clause([instanceMapper.get_literal_from_mapping(f'{0}_{states}')])

        #estado final 
        for states in satPlanInstance.get_final_state():
            formula.add_clause([instanceMapper.get_literal_from_mapping(f'{niveis}_{states}')])
        

        for i in range(niveis):

            #acoes
            clausula = [] 
            for acao in satPlanInstance.get_actions():
                clausula.append(instanceMapper.get_literal_from_mapping(f'{i}_{acao}'))
            formula.add_clause(clausula)
            #mas so uma delas
            for acao in range(len(clausula)):
                for acao1 in range(acao + 1,len(clausula)):
                    formula.add_clause([-clausula[acao], -clausula[acao1]])

            #tratando as pre-condiçoes
            for acao in satPlanInstance.get_actions():
                for pre in satPlanInstance.get_action_preconditions(acao):
                    if pre[0] == '~':
                        pre = pre.replace('~','')
                        formula.add_clause([-instanceMapper.get_literal_from_mapping(f'{i}_{acao}'), -instanceMapper.get_literal_from_mapping(f'{i}_{pre}')])
                    else: formula.add_clause([-instanceMapper.get_literal_from_mapping(f'{i}_{acao}'), instanceMapper.get_literal_from_mapping(f'{i}_{pre}')])
            
            #tratando as pos-condiçoes
            for acao in satPlanInstance.get_actions():
                for pos in satPlanInstance.get_action_posconditions(acao):
                    if pos[0] == '~':
                        pos = pos.replace("~","")
                        formula.add_clause([-instanceMapper.get_literal_from_mapping(f'{i}_{acao}'), -instanceMapper.get_literal_from_mapping(f'{i+1}_{pos}')])
                    else: 
                        formula.add_clause([-instanceMapper.get_literal_from_mapping(f'{i}_{acao}'), instanceMapper.get_literal_from_mapping(f'{i+1}_{pos}')])
                poscond = satPlanInstance.get_action_posconditions(acao)
                #acoes que nao serao afetadas para o prox nivel
                nafetados = [i for i in satPlanInstance.get_state_atoms() if i not in poscond and f'~{i}' not in poscond]
                for nafetado in nafetados:
                    formula.add_clause([-instanceMapper.get_literal_from_mapping(f'{i}_{nafetado}'), -instanceMapper.get_literal_from_mapping(f'{i}_{acao}'), instanceMapper.get_literal_from_mapping(f'{i+1}_{nafetado}') ])
                    formula.add_clause([instanceMapper.get_literal_from_mapping(f'{i}_{nafetado}'), -instanceMapper.get_literal_from_mapping(f'{i}_{acao}'), -instanceMapper.get_literal_from_mapping(f'{i+1}_{nafetado}') ])

        formula.solve()
        if formula.get_model() is not None:           
            for literal in formula.get_model():
                if literal < 0:
                    continue
                for acao in satPlanInstance.get_actions():
                    if acao in instanceMapper.get_literal_from_mapping_reverse(literal) :
                        print(instanceMapper.get_literal_from_mapping_reverse(literal))
                        break
            break

        niveis += 1