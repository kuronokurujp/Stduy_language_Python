# -*- coding: utf-8 -*-

###########################################################################
## Python code generated with wxFormBuilder (version 3.10.1-0-g8feb16b3)
## http://www.wxformbuilder.org/
##
## PLEASE DO *NOT* EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc
import wx.aui

###########################################################################
## Class base_frame
###########################################################################

class base_frame ( wx.Frame ):

	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 500,300 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

		self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

		layout = wx.BoxSizer( wx.VERTICAL )

		self.m_panel4 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		layout.Add( self.m_panel4, 1, wx.EXPAND |wx.ALL, 5 )

		self.note_book = wx.aui.AuiNotebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_BOTTOM )
		self.panel_Info_server = wx.Panel( self.note_book, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.note_book.AddPage( self.panel_Info_server, u"サーバー", False, wx.NullBitmap )
		self.panel_log = wx.Panel( self.note_book, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.note_book.AddPage( self.panel_log, u"操作履歴", True, wx.NullBitmap )

		layout.Add( self.note_book, 1, wx.EXPAND |wx.ALL, 5 )


		self.SetSizer( layout )
		self.Layout()
		self.status_bar = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )
		self.menu_bar = wx.MenuBar( 0 )
		self.menu_file = wx.Menu()
		self.menu_bar.Append( self.menu_file, u"ファイル (F)" )

		self.menu_visible = wx.Menu()
		self.menu_bar.Append( self.menu_visible, u"表示 (V)" )

		self.SetMenuBar( self.menu_bar )

		self.tool_bar = wx.aui.AuiToolBar( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_TB_HORZ_LAYOUT|wx.aui.AUI_TB_HORZ_TEXT|wx.aui.AUI_TB_PLAIN_BACKGROUND )
		self.tool_bar.SetForegroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT ) )
		self.tool_bar.SetBackgroundColour( wx.SystemSettings.GetColour( wx.SYS_COLOUR_HIGHLIGHTTEXT ) )

		self.btn_autotrade = self.tool_bar.AddTool( wx.ID_ANY, u"自動売買", wx.NullBitmap, wx.NullBitmap, wx.ITEM_NORMAL, wx.EmptyString, wx.EmptyString, None )

		self.tool_bar.Realize()


		self.Centre( wx.BOTH )

	def __del__( self ):
		pass


