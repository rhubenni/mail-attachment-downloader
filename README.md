# mail-attachment-downloader
Robô para download automático de anexos de e-mails

Essa aplicação conecta-se a um servidor IMAP, partindo da premissa de que a conta em questão é uma caixa de e-mail exclusiva para recebimento de anexos por meio deste processo.

Apenas as mensagens marcadas ainda como NÃO LIDAS (flag **\UNSEEN**) são capturadas e baixadas para uma pasta pré-definida, após a conclusão do processo, todas as mensagens da caixa são marcadas como lidas (flag **\SEEN**) e as que não correspondem a nenhuma regra de monitoramento são excluídas (flag **\DELETED**).

## Parametrização
Os arquivos _*-config.py_ contém as entradas para importantes pontos de configuração e devem ser alterados para que a aplicação possa funcionar corretamente:

#### _imap_config.py_
É aqui que definimos os dados de conexão ao servidor IMAP: Usuário, senha, serevidor e porta:

```python

# IMAP server info
IMAP_CONFIG = {
    'server':   'outlook.office365.com',
    'user':     'mail@server.com',
    'pass':     'Password!@123456',
    'port':     993
}

````

#### _pyodbc_config.py_
Neste arquivo definimos os dados de conexão ao servidor de banco de dados, para leitura das regras de e-mail e armazenamento de log. Os dados de conexão devem ser inseridos na _SQLSRV_CONFIG_ e os nomes das tabelas de regras e log em _SQLSRV_TABLES_:

```python

# SQLServer info
SQLSRV_CONFIG = {
    "server":   '10.0.0.0',
    "database": 'dbMyDatabase',
    "user":     'usrMyUser',
    "pass":     'usrMyPass',
    "appName":  ''
}

SQLSRV_TABLES = {
    "monitor_list": '', # A tabela com as regras
    "monitor_log":  '' # Registro de log
}

````

#### _proxy_config.py_
Em ambientes corporativos, não raro estamos por trás de servidores proxys com regras de autenticação. Neste arquivo, definimos se utilizaremos algum servidor proxy HTTP e os dados para autenticação do mesmo:

> Este aplicativo depende da lib _PySocks_ para uso com servidores proxy, porém, em alguns casos, a lib _PySocks_ pode não efetuar a autenticação corretamente quando utilizando um servidor proxy HTTP, neste caso, foi preciso fazer um fork da _PySocks_ com um pequeno _workaroud_ para contornar essa limitação. O uso desse fork (_[PySocks Extended](https://github.com/rhubenni/PySocksExtended/)_) pode ser definido pela flag **_USE_PYSOCKS_EXTENDED_**.

```python
# Proxy server info
PROXY = {
    'server':   '0.0.0.0',
    'port':     8080,
    'user':     'myusername',
    'pass':     'secret##123'
}

# Define PySocks Version (False = Classic Pysocks, True = Pysocks Extended)
USE_PYSOCKS_EXTENDED = True
````

## As Regras
As regras para filtro de e-mails e anexos que iremos monitorar e capturar devem ser inseridas na tabela informada em _SQLSRV_TABLES["monitor_list"]_ no arquivo _pyodbc_config.py_, cuja estrutura é a seguinte:

#### Estrutura da tabela de regras
```sql
USE [DatabaseName];
GO
CREATE TABLE [MailReaderApp].[MessageListMonitorRulesTable] (
	[RuleId] [int] IDENTITY(1,1) NOT NULL,
	[Sender] [varchar](256) NOT NULL,
	[SubjectText] [varchar](256) NOT NULL,
	[SubjectSearchMode] [varchar](10) NOT NULL,
	[ContentType] [varchar](256) NOT NULL,
	[AttachmentName] [varchar](256) NOT NULL,
	[AttachmentSearchMode] [varchar](10) NOT NULL,
	[SavePath] [varchar](256) NOT NULL,
	[Enabled] [bit] NOT NULL,
	CONSTRAINT [PK_MessageListMonitor] PRIMARY KEY CLUSTERED ([RuleId] ASC)
);

ALTER TABLE [MailReader].[MessageListMonitor]  WITH CHECK ADD CHECK  (([AttachmentSearchMode]='Equals' OR [AttachmentSearchMode]='Contains' OR [AttachmentSearchMode]='StartsWith' OR [AttachmentSearchMode]='EndsWith' OR [AttachmentSearchMode]='Regex'));
ALTER TABLE [MailReader].[MessageListMonitor]  WITH CHECK ADD CHECK  (([SubjectSearchMode]='Equals' OR [SubjectSearchMode]='Contains' OR [SubjectSearchMode]='StartsWith' OR [SubjectSearchMode]='EndsWith' OR [SubjectSearchMode]='Regex'));

````

#### Descrição dos campos

| Campo                | Descrição     | Observações |
| -------------        | ------------- | ----------- |
| RuleId               | Inteiro que representa a chave primária da tabela | _AUTO INCRMENT_ |
| Sender               | O endereço de e-mail esperado do rementente | Serão consideradas apenas mensagens enviadas por este endereço |
| SubjectText          | Texto esperado no assunto da mensagem | Este valor é avaliado como definido em _SubjectSearchMode_ |
| SubjectSearchMode    | Como a comparação da regra de assunto do e-mail deve ser feita | Os calores possíveis são: (Equals/Contains/StartsWith/EndsWith/Regex) |
| ContentType          | _MIME-Type_ esperado para o anexo | Essa função ainda não está implementada, quem sabe em uma versão futura? |
| AttachmentName       | O padrão de nome esperado para o anexo | Este valor é avaliado como definido em _AttachmentSearchMode_ |
| AttachmentSearchMode | Como a comparação da regra de nome do anexo deve ser feita | Os calores possíveis são: (Equals/Contains/StartsWith/EndsWith/Regex) |
| SavePath             | Caminho relativo onde os dados devem ser salvos | As subpastas serão criadas, caso não existam |
| Enabled              | BIT que indica se a regra está ativa ou não | 1 = True / 0 = False |


#### _SearchMode_ - O modo de pesquisa
Os seguintes valores são aceitos para os campos _SubjectSearchMode_ e _AttachmentSearchMode_, eles definem qual a lógica de pesquisa que será utilizada na comparação dos assuntos dos e-mails e dos nomes dos anexos:

| SearchMode           | Resultado eseprado |
| -------------        | ------------------ |
| Equals               | A regra será avaliada como _TRUE_ se o valor do e-mail recebido for exatamente igual ao valor da regra |
| Contains             | A regra será avaliada como _TRUE_ se o valor do e-mail contiver, em qualquer parte da string, o valor da regra |
| StartsWith           | A regra será avaliada como _TRUE_ se o valor do e-mail recebido for prefixado com a string da regra |
| EndsWith             | A regra será avaliada como _TRUE_ se o valor do e-mail recebido for sulfixado com a string da regra |
| Regex                | A regra será avaliada como _TRUE_ se o valor do e-mail recebido corresponder a expressão regular informada |

#### Onde os arquivos são salvos?
Os anexos capturados pelo processo são salvos no caminho definido no campo _SavePath_ da regra de e-mail, este caminho, por motivos de segurança, sempre será relativo a configuração **_ROOT_SAVEPATH_**, que deve ser definida no arquivo _mail-attachment-downloader.py_:

```python
ROOT_SAVEPATH = 'B://'
````

Dessa forma, uma regra que define que um arquivo deve ser salvo em _/AnexoDaRegra1/_ na verdade será salvo em _'B://AnexoDaRegra1//'_
