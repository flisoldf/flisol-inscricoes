# -*- coding: utf-8 -*-

@auth.requires_membership('Administrador')
def lista():
    """
    Lista todas as salas cadastradas
    """
    
    salas = db(db.sala.id > 0).select()
    
    return dict(salas=salas)
    
@auth.requires_membership('Administrador')
def nova():
    """
    Invoca o formulario de cadastro
    das salas
    """
    form = SQLFORM(db.sala,submit_button=T('Save'))
    
    if form.accepts(request.vars,session):
        session.flash = "Sala cadastrada com sucesso"
        redirect(URL('locais','lista'))
    elif form.errors:
        session.flash = "Erro ao cadastrar o Local"
    
    return dict(form=form)

@auth.requires_membership('Administrador')
def editar():
    """
    Edita a sala selecionada
    """
    
    # Captura seu ID
    id_sala = request.args(0) or redirect(URL('locais','lista'))
    
    # Ocultando o campo ID
    db.sala.id.readable = False
    
    form = SQLFORM(db.sala, id_sala,submit_button=T('Save'), deletable=True)
    
    if form.accepts(request.vars, session):
        session.flash = 'Registro atualizado com sucesso'
        redirect(URL('locais', 'lista'))
    elif form.errors:
        session.flash = "Erro ao cadastrar o Local"
    
    # Renderizando o form no arquivo nova.html
    response.view = 'locais/nova.html'
    
    return dict(form=form)
