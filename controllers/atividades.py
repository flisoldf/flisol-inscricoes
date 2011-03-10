# -*- coding: utf-8 -*-


@auth.requires_membership('Palestrante')
def index():
    """
    Exibe a lista de atividades submetidas
    """
    # Se não houver argumentos na URL, redireciona para a página inicial
    # O objetivo dessa verificação é não permitir que um palestrante visualize atividades de outro
    if not request.args:
        redirect(URL('default', 'index'))
    palestrante = request.args(0)
    id_user = str(session.auth.user.id)
    
    # Faz a consulta no banco de dados para pegar o id do currículo do palestrante
    curriculo_id = db(curriculo.id_usuario==session.auth.user.id).select().first()
    
    if curriculo_id:
    
        # Insere uma notificação para os palestrantes
        session.flash = "O prazo para a submissão de atividades é até o dia 18 de Março."    
    
        # Verifica se o argumento passado na URL é o mesmo da sessão do usuário
        if palestrante == id_user:
            ativ = db(atividade.id_usuario==palestrante).select()
            return dict(ativ=ativ, id_user=int(palestrante))
        elif form.errors:
            return dict(ativ=None, id_user=int(palestrante))        
    else:
        session.flash = "Escreva o seu mini-curriculo antes de cadastrar sua palestra."
        redirect(URL('atividades', 'minicurriculo'))

@auth.requires_membership('Palestrante')
def nova():
    """
    Essa função é para inserção de novas atividades
    """
    
    # Ocultando o campo status e a sala
    db.atividades.status.readable = \
    db.atividades.status.writable = False
    
    db.atividades.id_sala.readable = \
    db.atividades.id_sala.writable = False
    
    # Gera o formulário para inserir novas atividades
    form = SQLFORM(atividade,formstyle='divs',submit_button=T('Save'),_class='forms')
    
    # Captura o id do usuário logado no momento e popula no respectivo campo do formulário
    form.vars.id_usuario = session.auth.user.id
    
    # Faz a consulta no banco de dados para pegar o id do currículo do palestrante
    curriculo_id = db(curriculo.id_usuario==session.auth.user.id).select().first()
    
    # Popula o respectivo campo do id do currículo do usuário
    if not curriculo_id:
        redirect(URL('atividades', 'minicurriculo'))
    else:        
        form.vars.id_curriculo = curriculo_id.id
    
    # Popula o status da atividade: 0 = Rejeitado, 1 = Aprovado, 2 = Pendente
    form.vars.status = 'Pendente'
    
    # Verifica se os dados inseridos passam em todas as validações do banco de dados e formulário
    if form.accepts(request.vars, session):
        session.flash = "Atividade submetida com sucesso"
        redirect(URL('atividades', 'index', args=session.auth.user.id))
    elif form.errors:
        session.flash = "Erro ao inserir a Atividade. Abra o formulário e tente novamente."
        
    return dict(form=form)

@auth.requires_membership('Palestrante')
def editar():
    """
    Edita a palestra selecionada
    pelo palestrante.
    """
    
    # Capturando o ID da Atividade selecionada
    id_atividade = request.args(0) or redirect(URL('atividades','index'))
    
    # Ocultando o campo ID e o Status
    db.atividades.id.readable = \
    db.atividades.id.writable = False
    
    db.atividades.status.readable = \
    db.atividades.status.writable = False
    
    # Criando o formulario de edicao
    form = SQLFORM(db.atividades, id_atividade,formstyle='divs',submit_button=T('Save'),_class='forms')
    
    if form.accepts(request.vars, session):
        session.flash = "Atividade atualizado com sucesso."
        redirect(URL('atividades', 'index', args=session.auth.user.id))
    elif form.errors:
        session.flash = "Erro ao inserir a Atividade. Abra o formulário e tente novamente."
    
    return dict(form=form)
    
@auth.requires_membership('Palestrante')
def minicurriculo():
    """
    Essa função é para criar/atualizar mini-currículo
    """
    
    # Captura o id do usuário logado
    id_user = session.auth.user.id
    
    # Consulta no banco para pegar o currículo do palestrante, caso houver
    atualizar = db(curriculo.id_usuario==id_user).select().first()
    
    # Se houver mini-currículo cadastrado, retorna o formulário para atualização
    if minicurriculo:
        # Ocultando o ID
        db.curriculo.id.readable = db.curriculo.id.writable = False
        form = SQLFORM(curriculo, atualizar, submit_button=T('Save'))
        form.vars.id_usuario = id_user
        
    # Caso não houver, retorna o formulário para criação
    else:
        form = SQLFORM(curriculo,formstyle='divs',submit_button=T('Save'),_class='forms')
        form.vars.id_usuario = id_user
    
    # Verifica se os dados inseridos batem com todas as validações e redireciona para Index, caso esteja ok.
    if form.accepts(request.vars, session):
        session.flash = 'Currículo atualizado com sucesso'
        redirect(URL('default', 'index'))
    elif form.errors:
        session.flash = "Mini-currículo não foi cadastrado com sucesso. Tente novamente"
    
    return dict(form=form)
    
@auth.requires_membership('Administrador')
def detalhes():
    """
    Exibe todos os detalhes da atividade selecionada.
    Com isso somente dois campos serão exibidos para edição:
    
     - Status da Atividade;
     - Sala da Atividade;
    """
    id_atividade = request.args(0)
    
    # Pesquisa a atividade selecionada
    atividade = db(db.atividades.id == id_atividade).select().first()
    
    # Exibindo somente o campo status
    db.atividades.id.readable = False

    db.atividades.titulo.readable = \
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

    form = crud.update(db.atividades, id_atividade) 
    
    return dict(atividade = atividade, form = form)
    
def cancelar():
    """
    Cancela a atividade selecionada
    pelo palestrante.
    """
    
    # Captura o ID ou redireciona
    id_atividade = request.args(0) or redirect(URL('atividades','index'))
    
    # Cancela a atividade
    db(db.atividades.id == id_atividade).update(status='Cancelada')
    
    # Volta para a lista de atividades cadastradas
    redirect(URL('atividades','index'))
    
    # Exibe mensagem de sucesso
    session.flash = "Atividade cancelada com sucesso."
    
    return dict()
    
    
