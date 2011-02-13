# -*- coding: utf-8 -*-
#########################################################################
## Customizando o titulo da aplicação, subtitulo e menus
#########################################################################

response.title = 'FLISOL Inscrições'
# response.subtitle = T('customize me!')

response.meta.author = 'Bruno Barbosa e Gilson Filho'
response.meta.description = ''
response.meta.keywords = 'web2py, flisol, software livre, acsldf'
response.meta.generator = 'Web2py Enterprise Framework'
response.meta.copyright = 'Copyright 2011'

##########################################
## Criando seus menus
##########################################

if 'auth' in globals():
    # Verifica se algum usuario esta logado
    if not auth.is_logged_in():
        response.menu = [
            (T('Home'), False, URL(request.application,'default','index'), []),
            (T('Sobre o Evento'), False, URL(request.application,'default','index'), []),            
            ]        
    else:    # Caso estiver logado exibe os menus de acordo com sua permissao
        if auth.has_membership('Palestrante'):
            response.menu = [
                (T('Home'), False, URL(request.application,'default','index'), []),
                (T('Atividades'), False, URL(request.application,'default','index'), []),
                ]
        if auth.has_membership('Participante'):
                    response.menu = [
                        (T('Home'), False, URL(request.application,'default','index'), []),
                        (T('Atividades Inscritas'), False, URL(request.application,'default','index'), []),
                        (T('Certificados'), False, URL(request.application,'default','index'), [])
                        ]                


