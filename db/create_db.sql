USE [OS_tracker]
GO

/****** Object:  Table [dbo].[github]    Script Date: 1/3/2017 4:31:24 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

DROP TABLE [dbo].[github]
GO

CREATE TABLE [dbo].[github](
	[stargazers_count] [int] NULL,
	[updated_at] [varchar](MAX) NULL,
	[full_name] [varchar](MAX) NULL,
	[id] [int] NULL,
	[subscribers_count] [int] NULL,
	[network_count] [int] NULL,
	[has_pages] [varchar](MAX) NULL,
	[open_issues_count] [int] NULL,
	[watchers_count] [int] NULL,
	[size] [int] NULL,
	[homepage] [varchar](MAX) NULL,
	[fork] [varchar](MAX) NULL,
	[forks] [varchar](MAX) NULL,
	[open_issues] [varchar](MAX) NULL,
	[has_issues] [varchar](MAX) NULL,
	[has_downloads] [varchar](MAX) NULL,
	[watchers] [varchar](MAX) NULL,
	[name] [varchar](MAX) NULL,
	[language] [varchar](MAX) NULL,
	[url] [varchar](MAX) NULL,
	[created_at] [varchar](MAX) NULL,
	[pushed_at] [varchar](MAX) NULL,
	[forks_count] [int] NULL,
	[default_branch] [varchar](MAX) NULL,
	[date_measured] [datetime] NOT NULL
) ON [PRIMARY]

GO

ALTER TABLE [dbo].[github] ADD DEFAULT (getdate()) FOR [date_measured]
GO
