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
