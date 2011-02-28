# -*- coding: utf-8 -*-

@auth.requires_membership('Administrador')
def lista():
    """
    Lista todos os tipos de Atividades
    """
    # Consulta todos os tipos de atividades
    tipos_atividades = db(db.tipo_atividade.id > 0).select()
    
    return dict(tipos_atividades=tipos_atividades)
    
@auth.requires_membership('Administrador')
def nova():
    """
    Formulario de Cadastro de Tipos de Atividades
    """
    form = SQLFORM(db.tipo_atividade, submit_button=T('Save'))
    
    if form.accepts(request.vars, session):
        session.flash = "Tipo de Atividade cadastrado com sucesso"
        redirect(URL('tipoatividade','lista'))
    elif form.errors:
        session.flash = "Erro ao cadastrar o Tipo de Atividade"
    
    return dict(form=form)
    
@auth.requires_membership('Administrador')
def editar():
    """
    Atualizacao dos Tipos de Atividades
    """
    # Captura o ID do Tipo da Atividade
    id_tipo = request.args(0) or redirect(URL('tipoatividade','lista'))
    
    # Ocultando o ID
    db.tipo_atividade.id.readable = False
    
    form = SQLFORM(db.tipo_atividade, id_tipo, submit_button=T('Save'), deletable=True)

    # Renderizando no nova.html
    response.view = 'tipoatividade/nova.html'

    if form.accepts(request.vars, session):
        session.flash = "Tipo de Atividade atualizado com sucesso"
        redirect(URL('tipoatividade','lista'))    
    elif form.errors:
        session.flash = "Erro ao atualizar o Tipo de Atividade"
    return dict(form=form)
