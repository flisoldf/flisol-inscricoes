# -*- coding: utf-8 -*-

@auth.requires_membership('Administrador')
def dashboard():
    """
    Essa função é para listar todas as atividades inscritas
    no sistema. Elas serão separadas a partir do seu status.
    Primeiro ira consultar as atividades, pendentes e após isso
    as aprovadas e rejeitadas. Os seus resultados serão enviados para
    os objetos do tipo plugin (que refencia ao Power Table) e renderizá-las
    na view
    """
    
    # Consultando as atividades
    atividades = db(db.atividades.id > 0).select(orderby=db.atividades.tipo)
    
    # return dict(atividades = atividades)
    return dict(atividades = atividades)
