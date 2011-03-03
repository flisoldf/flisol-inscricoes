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
    
    if request.args(0) == 'palestrantes':
        # Consultando palestrantes
        # ID do Grupo 3 - Palestrante
        query = (db.usuarios.id > 0) & (db.usuarios.grupo == 3)
        usuarios = db(query).select()
    
    if request.args(0) == 'inscritos':
        # Consultando inscritos
        query = (db.usuarios.id > 0) & (db.usuarios.grupo == 2)
        usuarios = db(query).select()
    
    if request.args(0) == 'administradores':
        # Consultando administradores
        query = (db.usuarios.id > 0) & (db.usuarios.id != session.auth.user.id) & \
                (db.usuarios.grupo != 3) & (db.usuarios.grupo != 2)
        usuarios = db(query).select()

    return dict(usuarios=usuarios,tipo_usuario=request.args(0))
    

@auth.requires_membership('Administrador')
def novo():
    """
    Cria um novo usuario
    """
    
    form = SQLFORM(db.usuarios,submit_button=T('Save'))

    if form.accepts(request.vars, session):
        # Consulta o usuario registrado a partir do username
        user = db(db.usuarios.username == request.vars.username).select().first()
        id_group = request.vars.grupo

        # Insere o relacionamento entre o usuario e seu grupo de permissao
        auth.add_membership(id_group, user.id)
    
        session.flash = "Usuário cadastrado com sucesso."
        """
        Caso o usuario cadastrado foi o perfil
        Palestrante, por exemplo, redireciona para a
        lista de palestrantes, e assim vai de acordo
        com o perfil escolhido
        """
        if request.vars.grupo == 3:
            redirect(URL('usuarios','lista',args=['palestrantes']))
        elif request.vars.grupo == 1:
            redirect(URL('usuarios','lista',args=['administradores']))
    elif form.errors:
        session.flash = "Erro ao cadastrar o Usuário"
            
    return dict(form=form)

@auth.requires_membership('Administrador')
def editar():
    """
    Edita o usuário selecionado
    """
    id_user = request.args(0) or redirect(URL('usuarios','lista'))
    
    # Ocultando o ID
    db.usuarios.id.readable = \
    db.usuarios.id.writable = False
    
    form = SQLFORM(db.usuarios, id_user, submit_button=T('Save'))
    
    # Renderiza formulario no novo.html
    response.view = 'usuarios/novo.html'
    
    if form.accepts(request.vars,session):
        session.flash = "Usuário cadastrado com sucesso."
    elif form.errors:
        session.flash = "Erro ao cadastrar o usuário. Tente novamente."
    
    return dict(form=form)
    
@auth.requires(auth.has_membership('Administrador') or auth.has_membership('Participante'))
def detalhes():
    """
    Exibe os detalhes do usuario selecionado
    """
    id_usuario = request.args(0) or redirect(URL('usuarios','lista'))

    # Consultando o usuario selecionado
    query = db.usuarios.id == id_usuario
    usuario = db(query).select().first()

    # Pesquisa o mini curriculo do usuario        
    minicurriculo = db(db.curriculo.id_usuario == id_usuario).select().first()
    
    # Suas atividades cadastradas
    atividades = db(db.atividades.id_usuario == id_usuario).select()
    
    # Renderiza na view separada
    response.view = 'usuarios/detalhes_palestrante.html'
    
    return dict(usuario=usuario,minicurriculo=minicurriculo,atividades=atividades)
