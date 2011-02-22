# -*- coding: utf-8 -*-

@auth.requires_membership('Administrador')
def dashboard():
    """
    Essa função é para listar todas as atividades inscritas
    no sistema. Elas serão separadas a partir do seu status.
    Primeiro ira consultar as atividades, pendentes e após isso
    as aprovadas e rejeitadas. Os seus resultados serão enviados para
    os objetos do tipo plugin (que refencia ao Power Table) e renderizá-las
    na view
    """
    
    ################################################################################
    ##                Atividades Pendentes
    ################################################################################    
    
    # Consultando as atividades pendentes
    pendentes = db(db.atividades.status == 'Pendente').select()
    
    ################################################################################    
    ##                Atividades Aprovadas
    ################################################################################    
    
    # Consultando as atividades aprovadas
    aprovadas = db(db.atividades.status == 'Aprovada').select()
    
    ################################################################################    
    ##                Atividades Rejeitadas
    ################################################################################    
    
    # Consultando as atividades rejeitadas
    rejeitadas = db(db.atividades.status == 'Rejeitada').select()
    
    return dict(pendentes = pendentes, aprovadas = aprovadas, rejeitadas = rejeitadas)


@auth.requires_membership('Administrador')
def status():
    id_atividade = request.args(0) or redirect(URL('admin','dashboard'))

    # Exibindo somente o campo status
    db.atividades.id.readable = False

    db.atividades.titulo.writable = False

    db.atividades.descricao.readable = \
    db.atividades.descricao.writable = False

    db.atividades.nivel.readable = \
    db.atividades.nivel.writable = False

    db.atividades.tipo.readable = \
    db.atividades.tipo.writable = False

    db.atividades.duracao.readable = \
    db.atividades.duracao.writable = False

    db.atividades.tag.readable = \
    db.atividades.tag.writable = False

    db.atividades.arquivo.readable = \
    db.atividades.arquivo.writable = False

    db.atividades.materiais.readable = \
    db.atividades.materiais.writable = False

    db.atividades.observacoes.readable = \
    db.atividades.observacoes.writable = False

    db.atividades.checa_apresentacao.readable = \
    db.atividades.checa_apresentacao.writable = False

    atividade = SQLFORM(db.atividades, id_atividade, submit_button=T('Save'),formstyle='table3cols')
    
    if atividade.accepts(request.vars, session):
        session.flash = "Status alterado com sucesso"
        redirect(URL('admin','dashboard'))

    return dict(atividade = atividade)
