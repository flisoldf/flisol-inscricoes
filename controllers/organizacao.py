def calcula_minutos(hr=request.now.strftime('%H:%M:%S')):
    """
    Essa função faz a conversão de Horas e Minutos em Minutos em uma string no formato: %H:%M:%S
    """
    separa_horario = hr.split(':')
    horas = int(separa_horario[0])
    minutos = int(separa_horario[1])
    minutos += (horas*60)
    return minutos

@auth.requires_membership('Organização')
def cadastro():
    """
    Cria um novo usuario
    """
    db.usuarios.grupo.writable = \
    db.usuarios.grupo.readable = False
    form = SQLFORM(db.usuarios,submit_button=T('Save'))
    # Aqui o grupo é ocultado e salvo diretamente como Grupo 2, pois os membros da organização
    # Só podem adicionar novos participantes.
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
    # Verifica se o usuário que está sendo editado não é Administrador ou Palestrante
    editando = db(db.usuarios.id==id_user).select()
    if editando[0].grupo != 2:
        redirect(URL('organizacao', 'listar'))
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
    """
    Lista os usuários inscritos no evento e fornece a opção de realizar o checkin
    e/ou liberar o certificado após o tempo pré-estabelecido
    """
    # Consulta os usuários inscritos no evento
    query = (db.usuarios.id > 0) & (db.usuarios.grupo == 2)
    usuarios = db(query).select(orderby=db.usuarios.id)
    # Consulta se o usuário já efetuou sua confirmação no evento
    confirmacao = db().select(db.checkin.ALL)
    agora = calcula_minutos()
    p_ok = ['confirmacao']
    p_cert = ['certificado']
    for confirmado in confirmacao:
        if confirmado.hora_checkin:
            p_ok.append(confirmado.id_usuario) if agora - calcula_minutos(str(confirmado.hora_checkin)) >= 180 else None
        if confirmado.certificado == True:
            p_cert.append(confirmado.id_usuario)
    return dict(usuarios=usuarios, confirmacao=p_ok, certificado=p_cert)

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
    query_confirm = (db.checkin.id_usuario == usuario)
    confirmacao = db(query_confirm).select()
    # Guarda na variável horário, a hora em que foi realizado o checkin do usuário
    horario = confirmacao[0].hora_checkin if confirmacao else None
    # Verifica se o usuário já possui registro no sistema.
    agora = calcula_minutos()
    if horario and agora - calcula_minutos(str(horario)) >= 180:
        # Captura ID da confirmação do usuário na tabela checkin
        id_confirm = confirmacao[0].id

        # Oculta os campos ID e ID_USUARIO da tabela checkin
        db.checkin.id.writable = \
            db.checkin.id.readable = False
        db.checkin.id_usuario.writable = \
            db.checkin.id_usuario.readable = False
        # Verifica se o certificado já está habilitado para download,
        #   Caso positivo, transforma o checkin da hora em somente leitura
        if confirmacao[0].certificado == True:
            db.checkin.hora_checkin.writable = False
        # Retorna o formulário da tabela checkin para atualização e/ou liberação do certificado
        certificado = SQLFORM(db.checkin, id_confirm, submit_button='Salvar')
        # Preenche automaticamente o campo id_usuario da tabela checkin de acordo com o valor passado na URL
        certificado.vars.id_usuario = usuario
        if certificado.accepts(request.vars, session):
            session.flash = 'Registro atualizado'
            redirect(URL('organizacao', 'listar'))
        return dict(certificado=certificado, usuarios=check_user, confirmar=None)
    else:
        id_confirm = confirmacao[0].id if confirmacao else None
        # Oculta os campos certificado, id e id_usuario
        db.checkin.certificado.writable = \
            db.checkin.certificado.readable = False
        db.checkin.id_usuario.writable = \
            db.checkin.id_usuario.readable = False
        db.checkin.id.writable = \
            db.checkin.id.readable = False
        # Retorna o formulário da tabela checkin para preenchimento
        if not confirmacao:
            confirmar = SQLFORM(db.checkin, submit_button='Salvar')
        else:
            confirmar = SQLFORM(db.checkin, id_confirm, submit_button='Salvar')
        # Preenche automaticamente o campo id_usuario da tabela checkin de acordo com o valor passado na URL
        confirmar.vars.id_usuario = usuario
        confirmar.vars.hora_checkin = request.now.strftime('%H:%M:%S') if not horario else confirmar.vars.hora_checkin
        if confirmar.accepts(request.vars, session):    # Coloca em uma lista todos os IDs dos pa    # Coloca em uma lista todos os IDs dos participantes confirmadosrticipantes confirmados
            session.flash = 'Registro atualizado'
            redirect(URL('organizacao', 'listar'))
        return dict(confirmar=confirmar, usuarios=check_user, certificado=None)

@auth.requires(auth.has_membership('Administrador') or auth.has_membership('Organização'))
def lista_vazia():
    """
    Renderiza uma tabela vazia em PDF para preenchimento manual de todos os dados
    Plugin: Appreport by Lucas D'Avilla
    """
    html = response.render('organizacao/lista_vazia.html')
    return plugin_appreport.REPORT(html = html)

@auth.requires(auth.has_membership('Administrador') or auth.has_membership('Organização'))
def lista_participante():
    """
    Essa função retorna uma página e um formulário para escolher se deseja imprimir o total de participantes ou
    apenas a partir de um determinado ID.
    Plugin: Appreport by Lucas D'Avilla
    """
    form = FORM('Informe o ID: ', INPUT(_name='inscricao', requires=IS_NOT_EMPTY()), INPUT(_type='submit'))

    if form.accepts(request.vars, session):
        redirect(URL('organizacao', 'lista_apartir', args=[request.vars.inscricao]))
    return dict(form=form)

@auth.requires(auth.has_membership('Administrador') or auth.has_membership('Organização'))
def lista_todos():
    """
    Essa função renderiza o arquivo PDF com todos os participantes inscritos no evento
    Plugin: Appreport by Lucas D'Avilla
    """
    participantes = db(db.usuarios.grupo==2).select()
    html = response.render('organizacao/lista_todos.html', dict(participantes = participantes))
    return plugin_appreport.REPORT(html = html)

@auth.requires(auth.has_membership('Administrador') or auth.has_membership('Organização'))
def lista_apartir():
    """
    Essa função renderiza o arquivo PDF com os participantes inscritos no evento a partir de um ID.
    Plugin: Appreport by Lucas D'Avilla
    """
    apartir = request.args(0) or redirect(URL('organizacao', 'listar'))
    participantes = db((db.usuarios.grupo==2) & (db.usuarios.id>=apartir)).select()
    html = response.render('organizacao/lista_todos.html', dict(participantes = participantes))
    return plugin_appreport.REPORT(html = html)