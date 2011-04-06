# -*- coding: utf-8 -*-

"""
###########################################
###      Módulo de Participantes
###########################################
"""

class CalculaVagas:
    """
    Classe para calcular a quantidade de inscritos/vagas totais de cada atividade/sala
    Uso:
        minhasala = CalculaVagas(ID_da_atividade)
        minhasala.calcular()

        minhasala.vagas -> Retorno: 18/20

        minhasala.disponivel() -> Retorna True se houver lugares, e False se não.
    """
    def __init__(self, atividade):
        self.atividade  = atividade

    def calcular(self):
        # Consulta a quantidade de lugares total da sala
        lugares = db(db.atividades.id==self.atividade).select()

        # Consulta a quantidade de participantes inscritos na atividade selecionada
        participantes = db(db.controle.atividade==self.atividade).count()

        if lugares:
            # Define a variável vagas com a quantidade de inscritos/vagas totais na atividade. Ex. 18/20
            self.vagas = '%d/%d' %(participantes, lugares[0].id_sala.lugares)

            # Retorna a quantidade total de lugares da atividade
            self.lugares = lugares[0].id_sala.lugares - participantes

        else:
            # Se não houver salas cadastradas e/ou definidas nas atividades, retorna 0/0 para vagas
            # E retorna em lugares o valor 10000, ou seja, ilimitado por não haver definição.
            self.vagas = '0/0'
            self.lugares = '10000'

    def disponivel(self):
        # Calcula se ainda há lugares disponíveis na sala.
        if self.lugares > 0:
            return True
        else:
            return False


def index():
    """
    Essa função lista todas as atividades que o participante se inscreveu.
    """
    
    # As instrucoes comentadas abaixo é pelo motivo de não precisar mais
    # os cadastros de inscricoes
    #inscritos = db(db.controle.usuario==session.auth.user.id).select()
    #return dict(inscritos=inscritos)
    response.view = 'participante/sucesso_inscricao.html'
    return dict()

def atividades():
    """
    Essa função lista todas as atividades aprovadas no sistema.
    """

    # Verifica se o usuário já está inscrito na atividade
    inscricao = db(db.controle.usuario==session.auth.user.id).select()

    # Consultando atividades aprovadas
    aprovadas = db(db.atividades.status=='Aprovada').select()

    vagas = {}
    for aprovada in aprovadas:
        # Faz o cálculo de inscritos na atividade no formato inscritos/vagas totais
        lugar = CalculaVagas(aprovada.id)
        lugar.calcular()
        vagas[aprovada.id] = lugar.vagas

    return dict(aprovadas=aprovadas, vagas=vagas, inscricao=inscricao)

def inscricao():
    """
    Essa função serve para o participante poder se inscrever/desinscrever em uma ou mais atividades.
    """
    selecionada = request.args(1) or redirect(URL('participante', 'index'))

    ### Inscrever
    if request.args(0) == 'inscrever':
        """
        Inscrição em atividades
        """

        # Chama a classe CalculaVagas para verificar a quantidade de inscritos/vagas disponíveis na atividade
        vaga_atividade = CalculaVagas(selecionada)
        vaga_atividade.calcular()

        # Verifica se o usuário já está inscrito na atividade
        inscricao = db(db.controle.usuario==session.auth.user.id).select()

        atividade_usuario = [minhaatividade.atividade for minhaatividade in inscricao]
        atividade_selecionada = int(selecionada)
        for ativ in atividade_usuario:
            if ativ == atividade_selecionada:
                session.flash = 'Você já está inscrito nessa atividade'
                redirect(URL('participante', 'index'))

        # Verifica se ainda há vagas disponíveis na atividade selecionada
        if vaga_atividade.disponivel() == True:
            db.controle.insert(atividade = selecionada, usuario = session.auth.user.id)
            db.commit()
            session.flash = 'Inscrição realizada com sucesso!'
            redirect(URL('participante', 'index'))

        else:
            session.flash = 'Essa atividade está lotada!'
            redirect(URL('participante', 'index'))

    ### Desinscrever
    if request.args(0) == 'desinscrever':
        db((db.controle.usuario==session.auth.user.id)&(db.controle.atividade==selecionada)).delete()
        db.commit()
        session.flash = 'Desinscrição realizada com sucesso'
        redirect(URL('participante', 'index'))


def certificados():
    """
    Essa função serve para habilitar o download do certificado pelo participante.
    """
    return dict(message='Os certificados ainda não estão disponíveis para Download')

def questionario():
    """
    Essa função retorna o questionário tecnológico, para preenchimento obrigatório no primeiro login.
    """
    return dict()

def inscritos():
    """
    Função para gerar uma página com a quantidade total de inscritos no evento.
    """
    total = db(db.usuarios.id>0).count()
    return dict(total=total)