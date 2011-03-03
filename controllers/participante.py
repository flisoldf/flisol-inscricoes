# -*- coding: utf-8 -*-

"""
###########################################
###      Módulo de Participantes
###########################################
"""

def index():
    """
    Essa função lista todas as atividades que o participante se inscreveu.
    """

    ###
    ### ISSUE: Falta inserir link para se desinscrever da atividade
    ###
    
    inscritos = db(db.participantes.usuario==session.auth.user.id).select()
    return dict(inscritos=inscritos)

def atividades():
    """
    Essa função lista todas as atividades aprovadas no sistema.
    """

    ###
    ### ISSUE: Falta inserir link para se inscrever na atividade
    ###

    # Consultando atividades aprovadas
    aprovadas = db(db.atividades.status=='Aprovada').select()
    return dict(aprovadas=aprovadas)

def inscricao():
    """
    Essa função serve para o participante poder se inscrever/desinscrever em uma ou mais atividades.
    """
    return dict()

def certificados():
    """
    Essa função serve para habilitar o download do certificado pelo participante.
    """
    return dict()

def questionario():
    """
    Essa função retorna o questionário tecnológico, para preenchimento obrigatório no primeiro login.
    """
    return dict()