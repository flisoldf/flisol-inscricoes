# -*- coding: utf-8 -*-

from gluon.utils import hash

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
    Field('first_name', length=128, default=''),
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
custom_auth_table.first_name.requires = IS_NOT_EMPTY(error_message= T('is_empty'))
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
            
# Rotulo dos campos
custom_auth_table.first_name.label = T('Name')
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

### Carga inicial para criacao do Administrador
admin  = {
    'name':'Administrator',
    'username':'admin',
    'password':'admin123',
    'email':'admin@mail.com',
    'grupo':'1',    # ID do grupo Administrador (caso for outro, altere)
}

# Caso nao existir
user_admin = db(db.usuarios.username == admin['username']).select().first()
if not user_admin:
    id_user = db.usuarios.insert(
        first_name = admin['name'],
        username = admin['username'],
        email = admin['email'],
        password = hash(admin['password'], 'md5'), # Convertendo a senha no formado MD5
        grupo = admin['grupo']
    )
    db.commit()
    db.relacionamento.insert(user_id = id_user,group_id = 1)
    db.commit()


### Se o usuario for Administrador, ele pode querer adicionar outro Administrador.
### Com isso tem que verificar se o usuario logado tem permissoes para isso, ou seja
### participa do grupo Administrador
if 'auth' in globals():
    if session.auth:    
        if auth.has_membership('Administrador'):
            custom_auth_table.grupo.requires = IS_IN_DB(db,'grupos.id', 'grupos.role',
                zero=T('escolha_grupo'), error_message=T('is_choose'))
    else:
        # query = db.grupos.role != 'Administrador'
        query = (db.grupos.role != 'Administrador') & (db.grupos.role != 'Participante')
        custom_auth_table.grupo.requires = IS_IN_DB(db(query),
            'grupos.id', 'grupos.role', zero=T('escolha_grupo'), error_message=T('is_choose'))        

###########################################
# Tabela de Tipos de Atividades           #
###########################################
"""
Define o tipo de atividade que o palestrante irá ministrar (Palestra, Mini-Curso, Install Fest, etc.)
"""

tipo_atividade = db.define_table('tipo_atividade',
                Field('tipo'),
                Field('ativo', 'boolean', default=True),
                format='%(tipo)s')

# Validação da tabela tipo_atividade
tipo_atividade.tipo.requires = [
                                IS_NOT_EMPTY(error_message='Tipos: Mini-Curso, Palestra...'),
                                IS_NOT_IN_DB(db, 'tipo_atividade.tipo', error_message='Selecione um valor válido')
                                ]

###########################################
# Tabela das Salas                        #
###########################################
"""
Define as salas e a quantidade de lugares disponíveis em cada uma
"""
sala = db.define_table('sala',
                       Field('nome', default='sala'),
                       Field('lugares', 'integer', default=60))

# Validação dos dados da tabela sala
sala.nome.requires = IS_NOT_EMPTY(error_message='Digite um nome')
sala.lugares.requires = IS_NOT_EMPTY(error_message='Informe a quantidade de lugares disponíveis na sala')


###########################################
# Tabela de Materiais                     #
###########################################
"""
Define a tabela de materiais necessários para o palestrante (Computador, datashow, internet, etc.)
"""


materiais = db.define_table('materiais',
                Field('nome'),
                Field('ativo', 'boolean', default=True),
                format='%(nome)s')

# Validação da tabela Materiais
materiais.nome.requires = [
                           IS_NOT_EMPTY(error_message='Materiais: DataShow, Computador, Internet...'),
                           IS_NOT_IN_DB(db, 'materiais.nome')
                           ]


###########################################
# Tabela Duração da Atividade             #
###########################################

duracao = db.define_table('duracao',
                          Field('duracao', 'integer'),
                          Field('descricao',),
                          format='%(duracao)s %(descricao)s')

# Validação da tabela duracao
duracao.duracao.requires = [
                            IS_NOT_EMPTY(error_message='Digite a duração da atividade: 1, 2, ..., 8'),
                            IS_NOT_IN_DB(db, 'duracao.descricao')
                            ]

duracao.descricao.requires = IS_NOT_EMPTY(error_message='Digite a descrição: Horas, Minutos...')
                
###########################################
# Tabela Mini-Curriculo                   #
###########################################
"""
Define a Tabela Mini-Currículo do Palestrante
"""


curriculo = db.define_table('curriculo',
                Field('id_usuario', 'integer'),
                Field('mini_curriculo', 'text'))
             
# Validadores - Tabela Mini-Currículo
curriculo.id_usuario.writable=curriculo.id_usuario.readable=False
curriculo.mini_curriculo.requires = IS_NOT_EMPTY(error_message='Preencha seu Mini-Currículo')

                
###########################################
# Tabela de Atividades                    #
###########################################
"""
Tabela para inserção de atividades pelo palestrante
"""

atividade = db.define_table('atividades',
                Field('id_usuario', usuarios),
                Field('id_sala', 'integer'),
                Field('id_curriculo', 'integer'),
                Field('titulo'), # Título da atividade
                Field('descricao', 'text'), # Descrição da atividade
                Field('nivel', 'list:string'),
                Field('tipo', tipo_atividade), # Tipo da atividade: Palestra, Mini-Curso, etc.
                Field('duracao', duracao), # Duração da atividade (em horas)
                Field('tag', label='Palavras-Chave'), # Tags
                Field('arquivo', 'upload', label='Apresentação'), # Campo para envio da apresentação em PDF ou ODP
                Field('materiais', 'list:reference materiais', # Lista de materiais necessários para o palestrante
                      label='Precisa de algum desses materiais?'),
                Field('status', default='Pendente'), # Status da atividade: Rejeitada / Aprovada / Pendente
                Field('observacoes', 'text', label='Observações'),
                Field('checa_apresentacao', label='Você apresentou essa atividade em outro evento? Qual?'))
                
# Validadores - Tabela Atividades

atividade.arquivo.requires = IS_UPLOAD_FILENAME(extension='(pdf|odp)$', lastdot=True, error_message='Sua apresentação deve estar no formato ODP ou PDF')
atividade.descricao.requires = IS_NOT_EMPTY(error_message='Faça uma breve descrição da sua atividade')
atividade.tag.writable=atividade.tag.readable=False # Oculatando as palavras chave, para uso posterior
atividade.id_curriculo.writable=atividade.id_curriculo.readable=False
atividade.nivel.requires = IS_IN_SET(['Básico', 'Intermediário', 'Avançado'], zero='Selecione...', error_message='Selecione o nível de sua atividade: Básico, Intermediário ou Avançado')
atividade.id_sala.writable=atividade.id_sala.readable=False # Não permite a visualização nem edição do campo id_sala
atividade.titulo.requires = IS_NOT_EMPTY(error_message='Informe o título de sua atividade')
atividade.tipo.requires = IS_IN_DB(db, 'tipo_atividade.id', '%(tipo)s', zero='Selecione...', error_message='Tipo da atividade: Palestra, Mini-Curso, InstallFest...') # Preenche a lista tipo atividade
atividade.duracao.requires = IS_IN_DB(db, 'duracao.id', '%(duracao)s %(descricao)s', zero='Selecione...', error_message='Informe a duração da atividade')
atividade.id_usuario.writable=atividade.id_usuario.readable=False # Não permite a visualização nem edição do campo ID Usuário
atividade.status.requires = IS_IN_SET(['Pendente','Aprovada','Rejeitada'], zero='Selecione...', error_message='Selecione um status para a atividade')

crud.settings.auth = None                      # força autorizacao no CRUD