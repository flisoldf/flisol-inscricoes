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
    
    # Caso nao cadastrou o curriculo, redireciona para o cadastro
    print curriculo_id
    if curriculo_id:
        # Verifica se o argumento passado na URL é o mesmo da sessão do usuário
        if palestrante == id_user:
            ativ = db(atividade.id_usuario==palestrante).select()
            return dict(ativ=ativ, id_user=int(palestrante))
        else:
            return dict(ativ=None, id_user=int(palestrante))        
    else:
        session.flash = "Escreva o seu mini-curriculo antes de cadastrar sua palestra."
        redirect(URL('atividades', 'minicurriculo'))



@auth.requires_membership('Palestrante')
def nova():
    """
    Essa função é para inserção de novas atividades
    """
    
    # Gera o formulário para inserir novas atividades
    form = SQLFORM(atividade)
    
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
    form.vars.status = 2
    
    # Verifica se os dados inseridos passam em todas as validações do banco de dados e formulário
    if form.accepts(request.vars, session):
        session.flash = "Atividade submetida com sucesso"
        redirect(URL('atividades', 'index', args=session.auth.user.id))
        
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
        form = SQLFORM(curriculo, atualizar)
        form.vars.id_usuario = id_user
        
    # Caso não houver, retorna o formulário para criação
    else:
        form = SQLFORM(curriculo)
        form.vars.id_usuario = id_user
    
    # Verifica se os dados inseridos batem com todas as validações e redireciona para Index, caso esteja ok.
    if form.accepts(request.vars, session):
        session.flash = 'Currículo atualizado com sucesso'
        redirect(URL('default', 'index'))
    
    return dict(form=form)
