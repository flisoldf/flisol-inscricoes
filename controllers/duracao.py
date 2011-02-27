# -*- coding: utf-8 -*-

@auth.requires_membership('Administrador')
def lista():
    """
    Consulta todas as duracoes das atividades
    cadastradas.
    """
    
    # Consultando as duracoes (horas) cadastradas
    duracoes = db(db.duracao.id > 0).select()
    
    return dict(duracoes=duracoes)
    
@auth.requires_membership('Administrador')
def novo():
    """
    Renderiza o formulario
    de cadastro de duração
    """
    
    form = SQLFORM(db.duracao, formstyle='divs',submit_button=T('Save'),_class='forms')
    
    if form.accepts(request.vars,session):
        session.flash = "Duração cadastrado com sucesso."
        redirect(URL('duracao','lista'))
    else:
        session.flash = "Falha ao inserir a duração. Tente novamente."
    
    return dict(form=form)
    
@auth.requires_membership('Administrador')
def editar():
    """
    Edita a duracao selecionada
    """
    id_duracao = request.args(0) or redirect(URL('duracao','lista'))
    
    # Ocultando o ID
    db.duracao.id.readable = \
    db.duracao.id.writable = False
    
    form = SQLFORM(db.duracao, id_duracao, formstyle='divs',submit_button=T('Save'),_class='forms')
    
    if form.accepts(request.vars,session):
        session.flash = "Duração atualizado com sucesso."
        redirect(URL('duracao','lista'))
    else:
        session.flash = "Falha ao inserir a duração. Tente novamente."
    
    return dict(form=form)    
