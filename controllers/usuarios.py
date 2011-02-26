# -*- coding: utf-8 -*-

@auth.requires_membership('Administrador')
def lista():
    """
    Consultando e listando todos os usuários
    cadastrados.
    
    A listagem dos usuarios foi separado a partir
    dos argumentos recebidos pelos links do menu.
    Caso o argumento for igual ao palestrantes, 
    então listar todos os palestrantes do sistema,
    e assim por diante.
    
    """
    # Configurando o plugin Power Table
    table = plugins.powerTable
    table.uitheme = 'ui-lightness'
    table.dtfeatures['sPaginationType'] = 'scrolling'
    table.headers = 'labels'
    table.dtfeatures['sScrollY'] = '200'
    table.dtfeatures['sScrollX'] = '100%'
    table.keycolumn = 'usuarios.id'
    table.columns = ['usuarios.first_name','usuarios.username','usuarios.email']
    table.showkeycolumn = False
    table.truncate = 120    
    
    if request.args(0) == 'palestrantes':
        # Consultando palestrantes
        # ID do Grupo 3 - Palestrante
        query = (db.usuarios.id > 0) & (db.usuarios.grupo == 3)
        palestrantes = db(query).select()
        table.datasource = palestrantes
    
    if request.args(0) == 'inscritos':
        # Consultando inscritos
        pass
    
    if request.args(0) == 'administradores':
        # Consultando administradores
        query = (db.usuarios.id > 0) & (db.usuarios.id != session.auth.user.id) & \
                (db.usuarios.grupo != 3) & (db.usuarios.grupo != 2)
        administradores = db(query).select()
        table.datasource = administradores

    return dict(table = table.create())
    

@auth.requires_membership('Administrador')
def novo():
    return dict()

@auth.requires_membership('Administrador')
def editar():
    """
    Edita o usuário selecionado
    """
    id_user = request.args(0) or redirect(URL('usuarios','lista'))
    
    form = SQLFORM(db.usuarios, id_user, submit_button=T('Save'))
    
    return dict(form=form)
