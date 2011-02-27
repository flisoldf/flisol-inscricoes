# -*- coding: utf-8 -*-

@auth.requires_membership('Administrador')
def lista():
    """
    Lista todos os materiais
    cadastrados.
    """
    # Consultando todos os materiais
    materiais = db(db.materiais.id > 0).select()
    
    return dict(materiais=materiais)
    
@auth.requires_membership('Administrador')
def novo():
    """
    Exibe o formulario de Materiais
    """
    form = SQLFORM(db.materiais,formstyle='divs',submit_button=T('Save'),_class='forms')
    
    if form.accepts(request.vars,session):
        session.flash = "Material cadastrado com sucesso."
        redirect(URL('materiais','lista'))
    else:
        session.flash = "Erro ao inserir o material. Verifique os campos se estão corretos."
    
    return dict(form=form)
    
@auth.requires_membership('Administrador')
def editar():
    """
    Edita o material selecionado
    """
    
    # Captura o ID do Material
    id_material = request.args(0) or redirect(URL('materiais','lista'))
    
    # Oculta o ID
    db.materiais.id.readable = \
    db.materiais.id.writable = False
    
    form = SQLFORM(db.materiais, id_material, formstyle='divs',submit_button=T('Save'),_class='forms')
    
    # Renderiza na pagina de formulario
    response.view = 'materiais/novo.html'
    
    if form.accepts(request.vars,session):
        session.flash = "Material atualizado com sucesso."
        redirect(URL('materiais','lista'))
    else:
        session.flash = "Erro ao atualizar o material. Tente novamente."
    
    return dict(form=form)
