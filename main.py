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

    #mapeamento indo e voltando
    instanceMapper.add_list_of_literals_to_mapping(satPlanInstance.get_atoms())

    nivel = 0
    status = False #formula.solve()

    #estado inical
    for block_state in (instanceMapper.get_list_of_literals_from_mapping(satPlanInstance.get_initial_state())):
        formula.add_clause([block_state])
        print(block_state)

    for block_state_neg in satPlanInstance.get_state_atoms():
        if block_state_neg not in satPlanInstance.get_initial_state():
            formula.add_clause([-instanceMapper.get_literal_from_mapping(block_state_neg)])
            print(-instanceMapper.get_literal_from_mapping(block_state_neg))


    #estado final
    for block_state in instanceMapper.get_list_of_literals_from_mapping(satPlanInstance.get_final_state()):
        formula.add_clause([block_state])
        print(block_state)




    #passagem de nivel 
    # while status == False:
    #     nivel += 1
    #     # qual ação posso usar de acordo com as pre condiçoes que possuo
    #     for i in range(nivel):
    #         for acao in satPlanInstance.get_actions():
    #             for pre in satPlanInstance.get_action_preconditions(acao):
    #                 formula.add_clause([-instanceMapper.get_literal_from_mapping(pre), instanceMapper.get_literal_from_mapping(acao)])
                
    #             status = formula.solve()
    #             print(status)


    print(instanceMapper.mapping)
    print(satPlanInstance.get_actions())
    print(satPlanInstance.get_state_atoms())

    for acao in satPlanInstance.get_actions():
        for pre in satPlanInstance.get_action_preconditions(acao):
            print(acao)
            print(-instanceMapper.get_literal_from_mapping(pre))
            print(instanceMapper.get_literal_from_mapping(acao))
            formula.add_clause([-instanceMapper.get_literal_from_mapping(pre), instanceMapper.get_literal_from_mapping(acao)])
            print('------------------------------------------------------------')

    #o nivel serve para ver quantas vezes ele buscara uma açao
    #laço de repetição que escolhe qual ação pode ser usada pois oq tem sao suas pre condiçoes
    #atualiza o mapping com as pos condiçoes que ele possui
    #a cada ação escolhida o solve é ativado para ver se esta solucionando 
    #laço se repete ate dar true
    #quando dar true encontra significa que aquela é a o passo a passo de açoes usadas

    print(formula.solve())
    print(formula.get_model())





    # print(instanceMapper.mapping)
    # print('////////////////////')
    # print(aux)
    # print('////////////////////')
    # print(satPlanInstance.get_action_posconditions('pick-up_a'))
    # print(satPlanInstance.get_action_preconditions('pick-up_a'))



    # estado inical
    # print(instanceMapper.mapping)
    # print('////////////////////////')
    # estado_inicial = create_literals_for_level_from_list(0, satPlanInstance.get_initial_state())
    # print(estado_inicial)
    # instanceMapper.add_list_of_literals_to_mapping(estado_inicial)
    # print(instanceMapper.get_list_of_literals_from_mapping(estado_inicial))
    # print(instanceMapper.mapping)
    # for block_state in (instanceMapper.get_list_of_literals_from_mapping(estado_inicial)):
    #     formula.add_clause([block_state])
    #     print(block_state)
    # for block_state_neg in instanceMapper.mapping:
    #     if block_state_neg not in estado_inicial:
    #         formula.add_clause([-instanceMapper.get_literal_from_mapping(block_state_neg)])
    #         print(-instanceMapper.get_literal_from_mapping(block_state_neg))

    # print(instanceMapper.mapping)

    # # estado final
    # estado_final = satPlanInstance.get_final_state()
    # for block_state in estado_final:
    #     print(instanceMapper.get_literal_from_mapping(block_state))
    #     formula.add_clause([instanceMapper.get_literal_from_mapping(block_state)])


    # # pos 
    # for i in satPlanInstance.actions:
    #     formula.add_clause([instanceMapper.get_literal_from_mapping(i)])

    # print(instanceMapper.mapping)







    # estado_inicial = satPlanInstance.get_initial_state()
    # estado_final = satPlanInstance.get_final_state()
    # print(estado_inicial)
    # print(estado_final)

    # atomos = satPlanInstance.get_atoms()
    # print(atomos)



### estudos 
    # print(satPlanInstance.get_atoms())
    # print(satPlanInstance.get_state_atoms())

    # a = satPlanInstance.get_state_atoms()
    # a = satPlanInstance.get_action_posconditions("pick-up_b")
    # print(a)
    # b = instanceMapper.get_list_of_literals_from_mapping(a)
    # print(b)
    # # print(instanceMapper.get_literal_from_mapping_reverse(-8))
    # print(create_literals_for_level_from_list(5,a))
    # # print(create_state_from_literals(['holding_b','on_a_b'],satPlanInstance.get_atoms()))

### tudo

    
    # estado_inicial = satPlanInstance.get_initial_state()
    # estado_final = satPlanInstance.get_final_state()
    # print(estado_inicial)
    # print(estado_final)


##### original alexandre
#o codigo a seguir é exemplo de uso
    # satPlanInstance = SatPlanInstance(sys.argv[1])
    # instanceMapper  = SatPlanInstanceMapper()
    # instanceMapper.add_list_of_literals_to_mapping(satPlanInstance.get_atoms())
    # print(instanceMapper.mapping)
    # # a = satPlanInstance.get_state_atoms()
    # a = satPlanInstance.get_action_posconditions("pick-up_b")
    # # print('///////////////////')
    # # print(a)
    # b = instanceMapper.get_list_of_literals_from_mapping(a)
    # print(b)
    # print(instanceMapper.get_literal_from_mapping_reverse(-8))
    # print(create_literals_for_level_from_list(5,a))
    # print(create_literal_for_level(5,'on_a_b'))
    # print("/////////////////////////")
    # oi = create_state_from_literals(['holding_b','on_a_b'],satPlanInstance.get_atoms()) 

    #qual que quero que fique positivo, de quais(outros serao negados)
    # print(create_state_from_literals(['holding_b','on_a_b'],satPlanInstance.get_atoms()))