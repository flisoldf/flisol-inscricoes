@auth.requires_membership('Organização')
def cadastro():
    """
    Cria um novo usuario
    """

    db.usuarios.grupo.writable = \
    db.usuarios.grupo.readable = False
    
    form = SQLFORM(db.usuarios,submit_button=T('Save'))

    form.vars.grupo = 2

    if form.accepts(request.vars, session):
        # Consulta o usuario registrado a partir do username
        user = db(db.usuarios.username == request.vars.username).select().first()
        id_group = request.vars.grupo

        # Insere o relacionamento entre o usuario e seu grupo de permissao
        auth.add_membership(id_group, user.id)

        session.flash = "Usuário cadastrado com sucesso."

        redirect(URL('organizacao', 'cadastro'))
        

    return dict(form=form)

@auth.requires_membership('Organização')
def editar():
    """
    Edita o usuário selecionado
    """
    id_user = request.args(0) or redirect(URL('usuarios','lista'))

    # Ocultando o ID
    db.usuarios.id.readable = \
    db.usuarios.id.writable = False

    db.usuarios.grupo.writable = \
    db.usuarios.grupo.readable = False

    form = SQLFORM(db.usuarios, id_user, submit_button=T('Save'),deletable=True)

    # Renderiza formulario no novo.html
    response.view = 'usuarios/novo.html'

    if form.accepts(request.vars,session):
        session.flash = "Usuário cadastrado com sucesso."

    elif form.errors:
        session.flash = "Erro ao cadastrar o usuário. Tente novamente."

    return dict(form=form)

@auth.requires_membership('Organização')
def listar():

    # Consulta os usuários inscritos no evento
    query = (db.usuarios.id > 0) & (db.usuarios.grupo == 2)
    usuarios = db(query).select(orderby=db.usuarios.id)

    # Consulta se o usuário já efetuou sua confirmação no evento
    confirmacao = db().select(db.checkin.ALL)

    # Coloca em uma lista todos os IDs dos participantes confirmados

    ##################
    ### IMPORTANTE ###
    ##################

    # Colocar mais um condicional verificando se o usuário confirmou sua presença a mais de 3 horas

    ##################

    p_ok = ['confirmacao']
    for confirmado in confirmacao:
        p_ok.append(confirmado.id_usuario)
    
    return dict(usuarios=usuarios, confirmacao=p_ok)

@auth.requires_membership('Organização')
def checkin():
    """
    Essa função serve para os membros da organização do evento efetuarem o checkin
    dos participantes.

    Em um primeiro momento, ocorre a confirmação da presença do participante,
    após 3 horas, o participante deve voltar ao checkin e re-confirmar sua presença
    liberando assim o certificado para download imediatamente.
    """

    # Verificando o ID do usuário passado via URL
    usuario = request.args(0) or redirect(URL('organizacao', 'listar'))

    # Efetuando consulta no banco de dados para obter seu Nome.
    query = (db.usuarios.id == usuario)
    check_user = db(query).select()

    # Efetuando uma consulta na tabela checkin, para verificar se o usuário já
    #   confirmou sua participação no evento
    confirmacao = db(db.checkin.id_usuario == usuario).select()

    if confirmacao:
        # Captura ID da confirmação do usuário na tabela checkin
        id_confirm = confirmacao[0].id

        # Oculta os campos ID e ID_USUARIO da tabela checkin
        db.checkin.id.writable = \
            db.checkin.id.readable = False

        db.checkin.id_usuario.writable = \
            db.checkin.id_usuario.readable = False

        # Retorna o formulário da tabela checkin para atualização e/ou liberação do certificado
        certificado = SQLFORM(db.checkin, id_confirm, submit_button='Salvar')

        # Preenche automaticamente o campo id_usuario da tabela checkin de acordo com o valor passado na URL
        certificado.vars.id_usuario = usuario

        ##################
        ### IMPORTANTE ###
        ##################

        # Colocar mais um condicional verificando se o usuário confirmou sua presença a mais de 3 horas

        ##################

        if certificado.accepts(request.vars, session):
            session.flash = 'Confirmação do usuário efetuada com sucesso.'
            redirect(URL('organizacao', 'listar'))
            
        return dict(certificado=certificado, usuarios=check_user, confirmar=None)

    else:
        # Oculta os campos certificado e id_usuario
        db.checkin.certificado.writable = \
            db.checkin.certificado.readable = False

        db.checkin.id_usuario.writable = \
            db.checkin.id_usuario.readable = False

        # Retorna o formulário da tabela checkin para preenchimento
        confirmar = SQLFORM(db.checkin, submit_button='Salvar')

        # Preenche automaticamente o campo id_usuario da tabela checkin de acordo com o valor passado na URL
        confirmar.vars.id_usuario = usuario

        if confirmar.accepts(request.vars, session):
            session.flash = 'Certificado Liberado para Download'
            redirect(URL('organizacao', 'listar'))

        return dict(confirmar=confirmar, usuarios=check_user, certificado=None)
