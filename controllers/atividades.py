# -*- coding: utf-8 -*-


@auth.requires_membership('Palestrante')
def index():
    if not request.args:
        redirect(URL('default', 'index'))
    palestrante = request.args(0)
    id_user = str(session.auth.user.id)
    if palestrante == id_user:
        ativ = db(atividade.id_usuario==palestrante).select()
        return dict(ativ=ativ, id_user=int(palestrante))
    else:
        return dict(ativ=None, id_user=int(palestrante))



@auth.requires_membership('Palestrante')
def nova():
    form = SQLFORM(atividade)
    form.vars.id_usuario = session.auth.user.id
    form.vars.status = 2
    if form.accepts(request.vars, session):
        session.flash = "Atividade submetida com sucesso"
        redirect(URL('atividades', 'index', args=session.auth.user.id))
    return dict(form=form)