# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a samples controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html
    """
    
    if session.auth:
        if auth.has_membership('Palestrante'):
            redirect(URL('atividades','index',args=auth.user.id))
        if auth.has_membership('Administrador'):
            redirect(URL('admin','dashboard'))
        if auth.has_membership('Participante'):
            redirect(URL('participante', 'index'))
        if auth.has_membership('Organização'):
            redirect(URL('organizacao', 'listar'))
    else:
        redirect(URL('default','user',args='register'))
    
    return dict()

def user():    
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    
    # Caso estiver no formulario de registro
    # cria o formulario de cadastro
    if request.args(0) == 'register':
        form = SQLFORM(db.usuarios, submit_button=T('register'))
         
        # Se o cadastro foi efetuado com sucesso
        # Vincule ao grupo selecionado
        if form.accepts(request.vars, session):
            # Consulta o usuario registrado a partir do username
            user = db(db.usuarios.username == request.vars.username).select().first()
            id_group = request.vars.grupo
 
            # Insere o relacionamento entre o usuario e seu grupo de permissao
            auth.add_membership(id_group, user.id)
 
            # Exibe mensagem de sucesso
            response.flash = T('sucesso_login')
 
            # Redireciona para o login
            redirect(URL('user',args=['login']))
        elif form.errors:
            session.flash = "Erro ao registrar o usuário. Verifique os campos novamente."
    
    elif request.args(0) == 'profile':      # Se esta no perfil do usuario, captura os seus dados para editar caso for necessário.
        # Ocultando os campos ID, PERFIL e SENHA
        db.usuarios.id.readable = False
        db.usuarios.grupo.readable = \
        db.usuarios.grupo.writable = False
        db.usuarios.password.readable = \
        db.usuarios.password.writable = False        
         
        # Capturando os dados do usuario logado
        id_user = session.auth.user.id
        form = SQLFORM(db.usuarios, id_user, submit_button=T('Save'))
         
        if form.accepts(request.vars, session):
            response.flash = 'Perfil atualizado com sucesso.'
        elif form.errors:
            session.flash = "Erro ao atualizar o perfil. Tente novamente."
         
    else:  # Caso nao entrar nos casos acima passa o metodo padrao auth()
        form = auth()
         
    return dict(form=form)

def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()


