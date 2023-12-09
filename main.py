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

    niveis = 1
    status = False
    
    # primeiro nivel
    nivel1 = create_literals_for_level_from_list(1, satPlanInstance.get_atoms())
    instanceMapper.add_list_of_literals_to_mapping(nivel1)

    # estado inical
    for states in create_state_from_literals(satPlanInstance.get_initial_state(),satPlanInstance.get_state_atoms()):
            if states[0] == '~':
                formula.add_clause([-instanceMapper.get_literal_from_mapping(f'1_{states}')])
                print(-instanceMapper.get_literal_from_mapping(f'1_{states}'))
            else: 
                formula.add_clause([instanceMapper.get_literal_from_mapping(f'1_{states}')])
                print(instanceMapper.get_literal_from_mapping(f'1_{states}'))       
    
    while status == False:
        nivel = 1

        #criar todos os literais do proximo nivel
        niveln = create_literals_for_level_from_list(niveis+1, satPlanInstance.get_atoms())
        instanceMapper.add_list_of_literals_to_mapping(niveln)

        #estado final vai mudar toda vez que se aumenta de nivel, ele ira pro proximo
        for states in satPlanInstance.get_final_state():
            formula.add_clause([instanceMapper.get_literal_from_mapping(f'{niveis+1}_{states}')])
            print(instanceMapper.get_literal_from_mapping(f'{niveis+1}_{states}'))
        
        print(instanceMapper.mapping)

        for i in range(niveis):
            print('passei')

            #tratamento das acoes
            #ser escolhida uma ação por nivel
            clausula = [] 
            for acao in satPlanInstance.get_actions():
                clausula.append(instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'))
            formula.add_clause(clausula)
            print(clausula)
            #mas so uma delas
            for acao in range(len(clausula)):
                for acao1 in range(acao + 1,len(clausula)):
                    formula.add_clause([-clausula[acao], -clausula[acao1]])
                    print(-clausula[acao], -clausula[acao1])

            #tratando as pre-condiçoes
            for acao in satPlanInstance.get_actions():
                for pre in satPlanInstance.get_action_preconditions(acao):
                    formula.add_clause([-instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), instanceMapper.get_literal_from_mapping(f'{nivel}_{pre}')])
                    print(-instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), instanceMapper.get_literal_from_mapping(f'{nivel}_{pre}'))
            
            print('poscondd//////////////')
            #tratando as pos-condiçoes
            for acao in satPlanInstance.get_actions():
                for pos in satPlanInstance.get_action_posconditions(acao):
                    if pos[0] == '~':
                        pos = pos.replace("~","")
                        formula.add_clause([-instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), -instanceMapper.get_literal_from_mapping(f'{nivel+1}_{pos}')])
                        print(-instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), -instanceMapper.get_literal_from_mapping(f'{nivel+1}_{pos}'))
                    else: 
                        formula.add_clause([-instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), instanceMapper.get_literal_from_mapping(f'{nivel+1}_{pos}')])
                        print(-instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), instanceMapper.get_literal_from_mapping(f'{nivel+1}_{pos}'))

                #acoes que nao serao afetadas para o prox nivel
                nafetados = [i for i in satPlanInstance.get_state_atoms() if i not in pos]
                for nafetado in nafetados:
                    formula.add_clause([-instanceMapper.get_literal_from_mapping(f'{nivel}_{nafetado}'), -instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), instanceMapper.get_literal_from_mapping(f'{nivel+1}_{nafetado}') ])
                    formula.add_clause([instanceMapper.get_literal_from_mapping(f'{nivel}_{nafetado}'), -instanceMapper.get_literal_from_mapping(f'{nivel}_{acao}'), -instanceMapper.get_literal_from_mapping(f'{nivel+1}_{nafetado}') ])


            nivel += 1
            print(instanceMapper.mapping)
        print(f'///////////NIVEL É:   {nivel}   /////////')

        niveis += 1

        if formula.solve():
            print(formula.get_model())
            status = True