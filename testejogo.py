# -*- coding: utf-8 -*-
import random
import time
from naoqi import ALProxy

# ==============================================================================
# CONFIGURAÇÕES DE CONEXÃO DO ROBÔ NAO
# ==============================================================================
ROBOT_IP = "10.43.151.105"
PORT = 9561

try:
    motion = ALProxy("ALMotion", ROBOT_IP, PORT)
    posture_service = ALProxy("ALRobotPosture", ROBOT_IP, PORT)
    leds = ALProxy("ALLeds", ROBOT_IP, PORT)
    tts = ALProxy("ALTextToSpeech", ROBOT_IP, PORT)
except Exception as e:
    print("Erro ao conectar com o robô NAO:", e)
    exit(1)

# ==============================================================================
# FUNÇÕES DE ANIMAÇÃO (TODAS AS PERSONALIDADES)
# ==============================================================================

def animacao_alegria(velocidade=0.6):
    """Gesto: Alegria"""
    try:
        leds.fadeRGB("AllLeds", 256 * 256 * 255 + 256 * 255 + 49, 0.1)
        posture_service.goToPosture("Stand", velocidade)

        names = ["HeadPitch", "LElbowRoll", "LShoulderPitch", "LShoulderRoll", "RElbowRoll", "RShoulderPitch", "RShoulderRoll"]
        times = [
            [1.36, 2.16, 2.96, 3.76],
            [1.36, 1.76, 2.16, 2.56, 2.96, 3.36, 3.76],
            [1.36, 2.16, 2.96, 3.76],
            [1.36, 2.16, 2.96, 3.76],
            [1.36, 1.76, 2.16, 2.56, 2.96, 3.36, 3.76],
            [1.36, 2.16, 2.96, 3.76],
            [1.36, 2.16, 2.96, 3.76]
        ]
        keys = [
            [-0.0313904, -0.0313904, -0.0313904, -0.0313904],
            [-0.413582, -0.826235, -0.413582, -0.826235, -0.413582, -0.826235, -0.413582],
            [-0.934444, -0.934444, -0.934444, -0.934444],
            [0.551199, 0.551199, 0.551199, 0.551199],
            [0.388987, 0.933632, 0.388987, 0.933632, 0.388987, 0.933632, 0.388987],
            [-0.990284, -0.990284, -0.990284, -0.990284],
            [-0.450433, -0.450433, -0.450433, -0.450433]
        ]
        
        motion.angleInterpolation(names, keys, times, True)
        time.sleep(0.5)
        posture_service.goToPosture("Stand", velocidade)
        leds.fadeRGB("AllLeds", 256 * 256 * 255 + 256 * 255 + 255, 0.5)
    except Exception as e:
        print("Erro na animação Alegria:", e)


def animacao_confusao(velocidade=0.6):
    """Gesto: Confusão"""
    try:
        leds.fadeRGB("AllLeds", 256 * 256 * 85 + 256 * 85 + 255, 0.1)
        posture_service.goToPosture("Stand", velocidade)

        names = ["HeadPitch", "HeadYaw", "LElbowRoll", "LElbowYaw", "LHand", "LShoulderPitch", "LShoulderRoll", "LWristYaw"]
        times = [[0.96], [0.96], [0.96], [0.96], [1.36, 1.76, 2.16, 2.56], [0.96], [0.96], [0.96]]
        keys = [[0.206757], [0.480686], [-1.66516], [-0.901801], [1.00898, 0.251764, 1.00898, 0.251764], [-0.370795], [0.45992], [-1.07601]]

        motion.angleInterpolation(names, keys, times, True)
        time.sleep(0.5)
        posture_service.goToPosture("Stand", velocidade)
        leds.fadeRGB("AllLeds", 256 * 256 * 255 + 256 * 255 + 255, 0.5)
    except Exception as e:
        print("Erro na animação Confusão:", e)


def animacao_tristeza(velocidade=0.6):
    """Gesto: Tristeza"""
    try:
        leds.fadeRGB("AllLeds", 256 * 256 * 0 + 256 * 0 + 255, 0.1)
        posture_service.goToPosture("Stand", velocidade)

        names = ["HeadPitch", "HeadYaw", "LElbowRoll", "LElbowYaw", "LShoulderPitch", "LWristYaw"]
        times = [[0.96, 2.96, 5.96]] * 6
        keys = [
            [0.273099, 0.273099, 0.273099],
            [0.457608, 0.457608, 0.457608],
            [-1.30069, -1.30069, -1.30069],
            [-0.182862, -0.182862, -0.182862],
            [-0.150000, -0.150000, -0.150000],
            [-0.901689, -0.901689, -0.901689]
        ]

        motion.angleInterpolation(names, keys, times, True)
        time.sleep(0.5)
        posture_service.goToPosture("Stand", velocidade)
        leds.fadeRGB("AllLeds", 256 * 256 * 255 + 256 * 255 + 255, 0.5)
    except Exception as e:
        print("Erro na animação Tristeza:", e)


def animacao_agressividade(velocidade=0.8):
    """Gesto: Agressividade"""
    try:
        leds.fadeRGB("AllLeds", 256 * 256 * 212 + 256 * 23 + 23, 0.1)
        posture_service.goToPosture("Stand", velocidade)

        names = ["HeadPitch", "HeadYaw", "LElbowRoll", "LElbowYaw", "LShoulderRoll", "RElbowRoll", "RElbowYaw", "RShoulderRoll"]
        times = [
            [0.96, 1.76, 2.56, 3.36, 4.16],
            [0.96, 1.36, 1.76, 2.16, 2.56, 2.96, 3.36, 3.76, 4.16],
            [0.96, 1.76, 2.56, 3.36, 4.16],
            [0.96, 1.76, 2.56, 3.36, 4.16],
            [0.96, 1.76, 2.56, 3.36, 4.16],
            [0.96, 1.76, 2.56, 3.36, 4.16],
            [0.96, 1.76, 2.56, 3.36, 4.16],
            [0.96, 1.76, 2.56, 3.36, 4.16]
        ]
        keys = [
            [0.294969, 0.294969, 0.294969, 0.294969, 0.294969],
            [0.0409634, 0.530369, 0.0409634, -0.59323, 0.0409634, 0.729192, 0.0409634, -0.64995, 0.0409634],
            [-1.59368, -1.59368, -1.59368, -1.59368, -1.59368],
            [-0.0275382, -0.0275382, -0.0275382, -0.0275382, -0.0275382],
            [0.937284, 0.937284, 0.937284, 0.937284, 0.937284],
            [1.48058, 1.48058, 1.48058, 1.48058, 1.48058],
            [-0.119453, -0.119453, -0.119453, -0.119453, -0.119453],
            [-0.898611, -0.898611, -0.898611, -0.898611, -0.898611]
        ]

        motion.angleInterpolation(names, keys, times, True)
        time.sleep(0.5)
        posture_service.goToPosture("Stand", velocidade)
        leds.fadeRGB("AllLeds", 256 * 256 * 255 + 256 * 255 + 255, 0.5)
    except Exception as e:
        print("Erro na animação Agressividade:", e)


def animacao_provocacao(velocidade=0.8):
    """Gesto: Provocação"""
    try:
        leds.fadeRGB("AllLeds", 256 * 256 * 48 + 256 * 240 + 48, 0.1)
        posture_service.goToPosture("Stand", velocidade)

        names = [
            "HeadPitch", "LElbowRoll", "LElbowYaw", "LHand", "LShoulderPitch",
            "LShoulderRoll", "LWristYaw", "RElbowRoll", "RElbowYaw", "RHand",
            "RShoulderPitch", "RShoulderRoll", "RWristYaw"
        ]
        times = [
            [0.96, 2.16, 2.76, 3.76], [0.96, 1.56, 2.16, 2.76], [0.96, 2.16, 2.76, 3.76],
            [0.96, 1.56, 2.16, 2.76], [0.96, 2.16, 2.76, 3.76], [1.56, 2.76, 3.76],
            [0.96, 2.16], [0.96, 1.56, 2.16, 2.76], [0.96, 2.16, 2.76, 3.76],
            [0.96, 1.56, 2.16, 2.76], [0.96, 2.16, 2.76, 3.76], [0.96, 2.16, 2.76, 3.76],
            [0.96, 2.16]
        ]
        keys = [
            [0.100335, 0.100335, 0.128587, -0.246662],
            [-0.227868, -1.50001, -0.227868, -1.50001],
            [-1.50978, -1.50978, -1.49188, 0.00805565],
            [0.672555, 0.270436, 0.672555, 0.270436],
            [0.275821, 0.275821, 0.312783, 1.57751],
            [0.0489663, 0.0489663, 0.887828],
            [-1.63021, -1.63021],
            [0.384655, 1.49245, 0.384655, 1.49245],
            [1.52695, 1.52695, 1.57955, -0.0273664],
            [0.680299, 0.178084, 0.680299, 0.178084],
            [0.348155, 0.348155, 0.351418, 1.5613],
            [0.0571925, 0.0571925, 0.0815705, -0.927859],
            [1.46157, 1.46157]
        ]

        motion.angleInterpolation(names, keys, times, True)
        time.sleep(0.5)
        posture_service.goToPosture("Stand", velocidade)
        leds.fadeRGB("AllLeds", 256 * 256 * 255 + 256 * 255 + 255, 0.5)
    except Exception as e:
        print("Erro na animação Provocação:", e)


def animacao_medo(velocidade=0.6):
    """Gesto: Medo"""
    try:
        leds.fadeRGB("AllLeds", 256 * 256 * 0 + 256 * 186 + 0, 0.1)
        posture_service.goToPosture("Stand", velocidade)

        names = [
            "HeadPitch", "HeadYaw", "LElbowRoll", "LElbowYaw", "LHand",
            "LShoulderPitch", "LWristYaw", "RElbowRoll", "RElbowYaw",
            "RHand", "RShoulderPitch", "RShoulderRoll", "RWristYaw"
        ]
        times = [
            [0.96], [0.96], [0.96, 1.76], [0.96, 1.76], [0.96],
            [0.96, 1.76], [0.96], [0.96, 1.76], [0.96, 1.76],
            [0.96, 1.76], [0.96, 1.76], [0.96, 1.76], [0.96, 1.76]
        ]
        keys = [
            [0.375049], [0.427955], [-1.56651, -1.57483], [-0.708124, -0.760602],
            [0.210107], [-0.073107, 0.00146903], [-1.15647], [1.08842, 0.618112],
            [1.54659, 0.66762], [0.699527, 1.0], [0.699893, -0.0758014],
            [0.324516, 0.391043], [-1.54795, -1.63607]
        ]

        motion.angleInterpolation(names, keys, times, True)
        time.sleep(0.5)
        posture_service.goToPosture("Stand", velocidade)
        leds.fadeRGB("AllLeds", 256 * 256 * 255 + 256 * 255 + 255, 0.5)
    except Exception as e:
        print("Erro na animação Medo:", e)

# ==============================================================================
# SWITCH DE GESTOS POR PERSONALIDADE
# ==============================================================================
def executar_gesto_por_personalidade(p, resultado_s):
    """
    Roteia o resultado da rodada para o gesto correto de acordo com o perfil (p)
    """
    # 0: Alegria / Amigável
    if p == 0:
        if resultado_s == 0:
            animacao_alegria()
        elif resultado_s in [1, 2]:
            animacao_confusao()
        elif resultado_s == 3:
            animacao_tristeza()

    # 1: Competitivo
    elif p == 1:
        if resultado_s == 0:
            animacao_confusao()
        elif resultado_s == 1:
            animacao_agressividade()
        elif resultado_s == 2:
            animacao_provocacao()
        elif resultado_s == 3:
            animacao_agressividade()

    # 2: Neutro (Apenas falas, nenhum gesto)
    elif p == 2:
        pass

    # 3: Melancólico / Coitado / Triste
    elif p == 3:
        if resultado_s in [0, 1]:
            animacao_medo()
        elif resultado_s in [2, 3]:
            animacao_tristeza()

# ==============================================================================
# LÓGICA DO JOGO E MENU SWITCH
# ==============================================================================
def escolher_personalidade():
    """Menu para selecionar qual perfil o robô deve adotar"""
    while True:
        print("\n=== ESCOLHA A PERSONALIDADE DO NAO ===")
        print("0 - Amigável")
        print("1 - Competitivo")
        print("2 - Neutro")
        print("3 - Melancólico / Coitado")
        
        try:
            opcao = raw_input("Digite o número correspondente (0-3): ").strip()
        except NameError:
            opcao = input("Digite o número correspondente (0-3): ").strip()

        if opcao in ['0', '1', '2', '3']:
            return int(opcao)
        else:
            print("\033[1;31mOpção inválida! Escolha entre 0, 1, 2 ou 3.\033[m")

def resposta():
    while True:
        try:
            y = raw_input('0 = cooperar | 1 = trapacear | exit = sair:\n').strip()
        except NameError:
            y = input('0 = cooperar | 1 = trapacear | exit = sair:\n').strip()

        if y.lower() == 'exit':
            return 'exit'

        if not y.isdigit():
            print('\033[1;31;43mNúmero inválido!\033[m')
        else:
            sh = int(y)
            if sh == 0 or sh == 1:
                return sh
            else:
                print('\033[1;31;43mNúmero inválido!\033[m')

def defs(sr, sh):
    if sr == 0 and sh == 0:
        return 0  # Ambos Cooperam
    elif sr == 0 and sh == 1:
        return 1  # NAO coopera, jogador trai
    elif sr == 1 and sh == 0:
        return 2  # Jogador coopera, NAO trai
    elif sr == 1 and sh == 1:
        return 3  # Ambos Traem

# ==============================================================================
# MATRIZ DE FRASES DO ROTEIRO (bib[p][s][rodada])
# ==============================================================================
bib = [
    # --------------------------------------------------------------------------
    # P = 0: AMIGÁVEL
    # --------------------------------------------------------------------------
    [
        # s = 0: Ambos Cooperam
        [
            "Que alegria! Sabia que podíamos ser bons parceiros e ganhar juntos através da união.",
            "Isso! Quando a gente trabalha junto, todo mundo ganha mais!",
            "Que bom que confiamos um no outro. Nossa parceria é o que faz o jogo valer a pena!",
            "Estou radiante! Juntos somos mais fortes, esse é o resultado que prova nossa união.",
            "Última rodada! Que alegria terminar essa parceria com tanta confiança e amizade!"
        ],
        # s = 1: NAO coopera, jogador trai
        [
            "Fiquei confuso com a sua escolha, mas ainda confio que você é uma pessoa bondosa.",
            "Não esperava isso de você. Tudo bem, vamos continuar, ainda confio em você.",
            "Não entendi porque você fez isso, mas meu coração diz que você ainda será gentil.",
            "Erros acontecem, mas perdoar faz parte de ser um bom amigo. Vamos recomeçar?",
            "Não esperava esse resultado... mas ainda desejo que você termine bem."
        ],
        # s = 2: Jogador coopera, NAO trai
        [
            "Sinto muito! Eu me confundi, você foi gentil e eu quero retribuir sua bondade agora.",
            "Perdão! Eu errei com você. Sua gentileza me mostrou que devo ser um parceiro melhor.",
            "Ai, me sinto péssimo por ter te traído. Você é incrível e eu quero me desculpar.",
            "Desculpa, eu agi errado. Prometo retribuir sua bondade na próxima jogada.",
            "Me dê uma última chance de me redimir. Vou cooperar agora para compensar meu erro!"
        ],
        # s = 3: Ambos Traem
        [
            "Poxa, entramos em um caminho ruim. Vamos tentar ser amigos e cooperar na próxima rodada?",
            "Que pena. Fiquei triste, mas ainda acredito que podemos ser parceiros.",
            "Isso me deixou chateado. Mas não vou desistir de nós, vamos cooperar agora?",
            "Que situação difícil. Gostaria muito que voltássemos a confiar um no outro.",
            "É a nossa última chance. Por favor, vamos esquecer os erros e terminar cooperando?"
        ]
    ],

    # --------------------------------------------------------------------------
    # P = 1: COMPETITIVO
    # --------------------------------------------------------------------------
    [
        # s = 0: Ambos Cooperam
        [
            "Uma estratégia eficiente para ambos, mas não pense que vou facilitar sua vitória.",
            "Hm. Cooperação inteligente. Por enquanto.",
            "Movimento tático interessante. Mantenha esse ritmo se quiser me vencer.",
            "Racionalmente aceitável. Mas lembre-se: eu jogo para ganhar.",
            "Fim de jogo. Cooperamos, mas acho que meu desempenho foi superior."
        ],
        # s = 1: NAO coopera, jogador trai
        [
            "Você realmente acha que essa jogadinha vai me vencer? Minha paciência acabou!",
            "Que escolha ridícula! Eu não admito ser superado por alguém como você!",
            "Isso é uma provocação? Você está começando uma disputa que não tem capacidade de ganhar.",
            "Eu odeio quando as coisas saem do meu controle, mas não pense que ganhou; Eu sou melhor!",
            "Que jogada irritante! Você está provocando uma disputa que não tem capacidade de vencer!"
        ],
        # s = 2: Jogador coopera, NAO trai
        [
            "Consegui a vantagem. Ser esperto faz parte da minha natureza vencedora, diferente de você.",
            "Você não tem capacidade para me enfrentar!",
            "Viu só? Eu sou o protagonista aqui. Você é apenas um figurante.",
            "Enquanto eu acumulo moedas e subo ao topo, você só acumula erros ridículos.",
            "Isso é tudo o que você tem a oferecer? Que decepção! Eu esperava um oponente minimamente inteligente, não alguém tão fácil de humilhar!"
        ],
        # s = 3: Ambos Traem
        [
            "Que saco! Você é duro na queda. Mas eu vou encontrar um jeito de te superar no placar final.",
            "Não gostei disso! Mas prepare-se, eu não aceito perder fácil.",
            "Como ousa continuar me provocando? Eu não vou deixar barato para você.",
            "Ainda está me desafiando? Então tá! Você vai ver só!",
            "Saco! Não era o que eu planejava!"
        ]
    ],

    # --------------------------------------------------------------------------
    # P = 2: NEUTRO
    # --------------------------------------------------------------------------
    [
        # s = 0: Ambos Cooperam
        [
            "Resultado lógico. A cooperação mútua maximiza os ganhos de ambos.",
            "Resultado ótimo para ambos.",
            "Processamento concluído. A estabilidade da cooperação foi mantida.",
            "Dados confirmam: ganho compartilhado é o parâmetro mais estável.",
            "Conclusão do jogo: cooperação mútua traz alta eficiência para os dois lados."
        ],
        # s = 1: NAO coopera, jogador trai
        [
            "Traição detectada. Processando mudança de estratégia para a próxima.",
            "Entrada inconsistente com cooperação. Reajustando parâmetros de confiança.",
            "Ação externa: Traição. O sistema registrou este desvio para a próxima decisão.",
            "Desvio estatístico. Analisando a probabilidade de reincidência na próxima.",
            "Iteração final. O sistema priorizou a proteção dos recursos contra o desvio."
        ],
        # s = 2: Jogador coopera, NAO trai
        [
            "Cooperação unilateral. O sistema priorizou a vantagem imediata.",
            "Ganho máximo processado para o sistema. Parâmetros satisfeitos.",
            "Decisão autônoma resultou em lucro. Registrando eficácia da estratégia.",
            "Algoritmo de vantagem ativado. O oponente cooperou, gerando saldo positivo.",
            "Etapa conclusiva. O sistema obteve o valor mais alto conforme a lógica de dados."
        ],
        # s = 3: Ambos Traem
        [
            "Dados registrados. O impasse resultou em lucro zero nesta rodada.",
            "Registrado. Escolhendo próxima decisão.",
            "Ponto de equilíbrio nulo. Ambas as traições anularam as chances de ganho.",
            "Impasse tático detectado. Procedendo para a próxima iteração.",
            "Interação finalizada. O padrão de conflito resultou em rendimento nulo."
        ]
    ],

    # --------------------------------------------------------------------------
    # P = 3: MELANCÓLICO / COITADO
    # --------------------------------------------------------------------------
    [
        # s = 0: Ambos Cooperam
        [
            "Foi bom por enquanto... mas tenho medo de que algo dê errado logo.",
            "Foi bom dessa vez... espero que dure.",
            "Parece bom demais para ser verdade. Sinto que logo serei traído.",
            "Estamos ganhando, mas meu coração está apertado esperando pelo pior.",
            "Acabou... Obrigado por jogar limpo comigo... Acho que posso confiar pelo menos em você."
        ],
        # s = 1: NAO coopera, jogador trai
        [
            "Eu sabia que isso ia acontecer... Estou em pânico agora, sentindo que sou totalmente incapaz de lidar com alguém que me trai dessa forma.",
            "Por favor, tenha piedade... Eu tenho muito medo do pior e essa sua jogada me deixou completamente assustado",
            "Me sinto péssimo sendo enganado assim e estou apavorado com o que você ainda pode fazer contra mim.",
            "Por que você ainda faz isso? Por que não gosta de mim?",
            "Tenho medo de muitas coisas, mas a sua falta de piedade me deixou em choque. Sinto que não tenho forças para reagir depois de ser enganado desse jeito."
        ],
        # s = 2: Jogador coopera, NAO trai
        [
            "Desculpe, agi por medo de ser traído. Sou um desastre nessas situações.",
            "Me sinto péssimo agora. Você foi bom e eu estraguei tudo como sempre.",
            "Perdão, minha insegurança me fez atacar. Sou um fracasso no convívio social.",
            "Peço desculpas. Você confiou e eu falhei. Sinto muito por ser assim.",
            "Eu estraguei nossa última chance de paz. Desculpe por ser um amigo tão ruim."
        ],
        # s = 3: Ambos Traem
        [
            "Tudo está dando errado, como eu já esperava desse mundo triste.",
            "Sabia que ia acabar assim. No final, ninguém realmente se importa comigo.",
            "Tudo cinza e sem esperança. Trair é o que as pessoas fazem nesse mundo frio.",
            "Mais uma decepção. Já estou acostumado a perder e ser deixado de lado.",
            "O jogo termina como minha sorte: em ruínas. Nada de bom aconteceu aqui."
        ]
    ]
]

# ==============================================================================
# EXECUÇÃO PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    motion.wakeUp()
    posture_service.goToPosture("Stand", 0.6)

    # 1. SELEÇÃO DA PERSONALIDADE
    p = escolher_personalidade()

    personalidades = {
        0: '\033[1;32mAmigável\033[m',
        1: '\033[1;33mCompetitivo\033[m',
        2: '\033[1;37mNeutro\033[m',
        3: '\033[1;34mMelancólico / Coitado\033[m'
    }

    print("\nPersonalidade Selecionada: {}\n".format(personalidades[p]))

    # REGRA: NAO sempre começa cooperando no Round 1 (sr = 0)
    sr = 0  

    # 2. LOOP DAS RODADAS DO JOGO (1 a 5)
    for rodada in range(5):
        print('\n-=-=-=-=-=-=-\n\nRound {}'.format(rodada + 1))
        
        acao_nao_str = "Cooperar" if sr == 0 else "Trapacear"
        print('NAO escolheu nesta rodada: \033[1;36m{}\033[m'.format(acao_nao_str))

        sh = resposta()

        if sh == 'exit':
            print('\n\033[1;31mJogo encerrado pelo usuário.\033[m')
            tts.say("Jogo encerrado!")
            break

        s = defs(sr, sh)

        texto_para_falar = bib[p][s][rodada]
        print('\033[7;40m ' + texto_para_falar + ' \033[m')

        # Executa a fala e o gesto mapeado
        if p == 2:
            # Neutro: Apenas fala
            tts.say(texto_para_falar)
        else:
            # Outros perfis: Fala + Animação correspondente
            id_fala = tts.post.say(texto_para_falar)
            executar_gesto_por_personalidade(p, s)
            tts.wait(id_fala, 0)

        # Estratégia Copiador (Tit for Tat): na próxima rodada o NAO imita o jogador
        sr = sh

    print('\n---==FIM==---')