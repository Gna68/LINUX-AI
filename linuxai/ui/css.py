APP_CSS = """
Screen { layout: vertical; }
#header { height: 1; padding: 0 2; background: $boost; display: none; }
#hero { height: 1fr; width: 100%; content-align: center middle; text-align: center; }
#chat { height: 1fr; display: none; padding: 0 2; }
#suggest { height: auto; max-height: 11; margin: 0 1; padding: 0 1; background: $boost; display: none; }
.msg { width: 100%; margin: 0 0 1 0; }
#hints { height: 1; padding: 0 2; color: $text 60%; }
#prompt { margin: 0 1; }
#status { height: 1; padding: 0 2; color: $text 60%; }
ModalScreen { align: center middle; background: $background 70%; }
#dialog { width: 64; max-width: 90%; height: auto; max-height: 85%; background: $panel; padding: 1 2; }
#dlg-head { height: 1; margin-bottom: 1; }
#dlg-title { width: 1fr; text-style: bold; }
#dlg-esc { width: auto; color: $text 50%; }
#dlg-search, #dlg-input { border: none; background: $panel; padding: 0; margin-bottom: 1; }
#dlg-list { border: none; background: $panel; height: auto; max-height: 14; padding: 0; }
#dlg-hint { color: $text 60%; margin-top: 1; }
"""
