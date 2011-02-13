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
    response.flash = T('You are successfully running web2py.')
    return dict(message=T('Hello World'))

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
        form = SQLFORM(db.usuarios)
        
        # Se o cadastro foi efetuado com sucesso
        # Vincule ao grupo selecionado
        if form.accepts(request.vars, session):
            # Consulta o usuario registrado a partir do username
            user = db(db.usuarios.username == request.vars.username).select().first()
            id_group = request.vars.grupo
            print user.id
            print id_group
            auth.add_membership(id_group, user.id)

            # Redireciona para a home
            response.view = 'default/index.html'

            # Exibe mensagem de sucesso
            response.flash = T('sucesso_login')
    
    elif request.args(0) == 'profile':      # Se esta no perfil do usuario, captura os seus dados para editar caso for necessário.
        # Ocultando os campos ID e PERFIL
        db.usuarios.id.readable = False
        db.usuarios.grupo.readable = \
        db.usuarios.grupo.writable = False
        
        # Capturando os dados do usuario logado
        id_user = session.auth.user.id
        form = SQLFORM(db.usuarios, id_user)
    
    else:       # Caso nao entrar nos casos acima passa o metodo padrao auth()
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


