# tvschedule

各局の公式サイトで公開されている番組表から番組情報を取得します

## 詳細
- `channels`

  各チャンネルの番組表を取得するためのクラスが含まれます
- `tvschedule`

  `channels`の使用例です
  
## 使用例
    import datetime
    import channels
    
    # TokyoMXの番組情報を保持するオブジェクト
    tmx = channels.TokyoMX()
    
    # 2018年7月13日の番組情報を取得
    tmx.fetch('20180713')
    
    # 2018年7月13日の19:30に放送している番組の取得
    program = tmx.program_at('20180713', '1930')
    
    # 番組情報の表示
    for k, v in program:
        print k + ': ' + v
    
## 使用
    import channels 
- `Channel`クラス
  
  各テレビ局の番組情報を保持するためのクラスに共通の親クラスです
