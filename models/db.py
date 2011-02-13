# -*- coding: utf-8 -*-
#########################################################################
## Preparando o ambiente para GAE ou não
#########################################################################

if request.env.web2py_runtime_gae:            # Caso estiver executando o ambiente GAE
    db = DAL('gae://mynamespace')             # conecta ao Google BigTable
    session.connect(request, response, db = db) # e armazene sessões e tickets aqui
    
    ### ou use as seguintes linhas para armazenar sessoes no Memcache
    from gluon.contrib.memdb import MEMDB
    from google.appengine.api.memcache import Client
    session.connect(request, response, db = MEMDB(Client()))
else:                                         # senao, use um banco de dados relacional
    db = DAL('sqlite://flisol_inscricao.sqlite')

## Caso não precisar mais da sessão
# session.forget()

## Importando as ferramentas adicionais
from gluon.tools import *
mail = Mail()                                  # E-mail
auth = Auth(globals(),db)                      # Autenticacao/Autorizacao
crud = Crud(globals(),db)                      # para helpers CRUD usando Auth
service = Service(globals())                   # para renderizacao json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()                      # Gerencia todos os plugins instalados no sistema

# Dados para envio de emails
mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # seu servidor SMTP
mail.settings.sender = 'you@gmail.com'         # seu email
mail.settings.login = 'username:password'      # suas credenciais ou vazio (caso nao precise de autenticacao)


# Antes de mais nada, temos que renomear as tabelas do modulo de autenticacao e controle de acesso
auth.settings.table_user_name = 'usuarios'
auth.settings.table_group_name = 'grupos'
auth.settings.table_membership_name = 'relacionamento'
auth.settings.table_permission_name = 'autorizacao'
auth.settings.table_event_name = 'eventos'

### Tabela grupos (customizado)
grupos = db.define_table(
    auth.settings.table_group_name,
    Field('role',length=128,default=''),
    Field('description',length=128,default=''),
    format='%(grupo)s')
    
custom_group_table = grupos
custom_group_table.role.requires = IS_NOT_EMPTY(error_message = T('is_empty'))
custom_group_table.description.requires = IS_NOT_EMPTY(error_message = T('is_empty'))

### Desabilitando a criacao automatica de grupos
auth.settings.create_user_groups = False

### Carga inicial de grupos
### Caso os grupos nao foram cadastrados, sao inseridos automaticamente
papeis = ('Administrador','Participante','Palestrante')

for papel in papeis:
    grupo = db(db.grupos.role == papel).select().first()
    if not grupo:
        db.grupos.insert(role=papel,description='Grupo tipo %s'%papel)

### Tabela usuarios (customizado)

usuarios = db.define_table(
    auth.settings.table_user_name,
    Field('name', length=128, default=''),
    Field('username', length = 128, default = '', unique = True),
    Field('email', length=128, default=''),
    Field('password', 'password', length=512,
          readable=False, label='Password'),
    Field('grupo', db.grupos, notnull = True),
    Field('registration_key', length=512,
          writable=False, readable=False, default=''),
    Field('reset_password_key', length=512,
          writable=False, readable=False, default=''),
    Field('registration_id', length=512,
          writable=False, readable=False, default=''),
    format='%(usuario)s')

# Validacao dos campos
custom_auth_table = usuarios
custom_auth_table.name.requires = IS_NOT_EMPTY(error_message= T('is_empty'))
custom_auth_table.username.requires = [
            IS_NOT_EMPTY(error_message = T('is_empty')),
            IS_NOT_IN_DB(db, custom_auth_table.username, T('login_already'))]
custom_auth_table.password.requires = [
            # Especifica a complexidade da senha
            # minimo = 6
            # caracteres especiais = 0 (nenhum)
            # caracteres em maiusculo = 0 (nenhum)
            IS_STRONG(min = 6, special = 0, upper = 0, invalid=' "', error_message = T('error_password')),CRYPT()]
custom_auth_table.email.requires = [IS_EMAIL(error_message=auth.messages.invalid_email)]
custom_auth_table.grupo.requires = IS_IN_DB(db(db.grupos.role != 'Administrador'),
    'grupos.id', 'grupos.role', zero=T('escolha_grupo'), error_message=T('is_choose'))

# Rotulo dos campos
custom_auth_table.name.label = T('Name')
custom_auth_table.username.label = T('Username')
custom_auth_table.email.label = T('Email')
custom_auth_table.password.label = T('Password')
custom_auth_table.grupo.label = T('Perfil')

auth.define_tables()                           # cria todas as tabelas necessarias para o modulo Auth
auth.settings.hmac_key = 'sha512:1d718a94-81cf-4274-8ac1-42207b203246'   # antes de define_tables()
auth.settings.mailer = mail                    # para verificação de email

# Habilitando verificacao de senha e desabilitando aprovacao de cadastro
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False

# Traduzindo o rotulo do campo Submit
auth.messages.submit_button = T('Submit')

crud.settings.auth = None                      # força autorizacao no CRUD
