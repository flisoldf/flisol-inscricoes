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
    
    # Consultando as atividades
    atividades = db(db.atividades.id > 0).select(orderby=db.atividades.tipo)
   
    # Configurando o plugin Power Table
    table = plugins.powerTable
    table.datasource = atividades
    table.uitheme = 'ui-lightness'
    table.dtfeatures['sPaginationType'] = 'scrolling'
    table.headers = 'labels'
    table.dtfeatures['sScrollY'] = '200'
    table.dtfeatures['sScrollX'] = '100%'
    table.keycolumn = 'atividades.id'
    table.columns = ['atividades.titulo','atividades.id_usuario','atividades.nivel','atividades.tipo','atividades.materiais','atividades.status']
    table.showkeycolumn = False
    table.truncate = 120       
    
    # Consultando as atividades rejeitadas
    rejeitadas = db(db.atividades.status == 'Rejeitada').select()
    
    # return dict(atividades = atividades)
    return dict(atividades = table.create())


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
