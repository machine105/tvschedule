# tvschedule

各局の公式サイトで公開されている番組表から番組情報を取得できます
現在はテレビ東京・TOKYO MXに対応しています

## 詳細
開発環境: python 2.7.15
- `channels`

  各チャンネルの番組表を取得するためのクラスが含まれます
- `tvschedule`

  `channels`の使用例です．簡易的な番組表を出力します
  
## 使用例
    import channels
    
    # TokyoMXの番組情報を保持するオブジェクト
    tmx = channels.TokyoMX()
    
    # 2018年7月13日の番組情報を取得
    tmx.fetch('20180713')
    
    # 2018年7月13日の19:30に放送している番組の取得
    program = tmx.program_at('20180713', '1930')
    
    # 番組情報の表示
    for k, v in program.items():
        print k + ': ' + str(v)
