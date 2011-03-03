# -*- coding: utf-8 -*-

from datetime import date, datetime

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

# Caso o prazo de inscricoes estoure, então desabilita a inscrição de palestrantes
hoje = date.today()
prazo_atividade = date(2011, 3, 18)

##########################################
## Criando seus menus
##########################################

if 'auth' in globals():
    # Verifica se algum usuario esta logado
    if not auth.is_logged_in():
        response.menu = [
            #(T('Home'), False, URL(request.application,'default','index'), []),
            #(T('Sobre o Evento'), False, 'http://flisoldf.blog.br/2011/?page_id=11', []),            
            ]        
    else:    # Caso estiver logado exibe os menus de acordo com sua permissao
        if auth.has_membership('Administrador'):
            response.menu = [
                    (T('Home'), False, URL('admin','dashboard'), []),
                    (T('Locais'), False, URL('locais','lista'), []),
                    (T('Tipo Atividade'), False, URL('tipoatividade','lista'), []),
                    (T('Cadastro Materiais'), False, URL('materiais','lista'), []),                    
                    # (T('Cadastro Duracao'), False, URL('duracao','lista'), []),                       
                    (T('Cadastro Usuarios'), False, None, [
                        (T('Usuario'), False, URL('usuarios','novo'), []),                    
                        (T('Inscritos'), False, URL('usuarios','lista', args=['inscritos']), []),
                        (T('Palestrantes'), False, URL('usuarios','lista', args=['palestrantes']), []),
                        (T('Administradores'), False, URL('usuarios','lista', args=['administradores']), [])
                    ])                                  
					]
        if auth.has_membership('Palestrante'):
            if hoje <= prazo_atividade:
                response.menu = [
                    (T('Home'), False, URL(request.application,'atividades','index'), []),
                    (T('Atividades'), False, URL(request.application,'atividades','nova'), []),
                    (T('Mini-Currículo'), False, URL(request.application, 'atividades', 'minicurriculo'), [])
                    ]
            else:
                response.menu = [
                    (T('Home'), False, URL(request.application,'atividades','index'), []),
                    (T('Mini-Currículo'), False, URL(request.application, 'atividades', 'minicurriculo'), [])
                    ]           
        if auth.has_membership('Participante'):
                    response.menu = [
                        (T('Home'), False, URL(request.application,'default','index'), []),
                        (T('Atividades Inscritas'), False, URL(request.application,'default','index'), []),
                        (T('Certificados'), False, URL(request.application,'default','index'), [])
                        ]                


