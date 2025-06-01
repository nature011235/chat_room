![alt text](detect_img/image-1.png)
這個因為沒清理到之前測試的數據

![alt text](detect_img/image.png)
多等一下就好了

![alt text](detect_img/image-2.png)
確實會有問題 沒有防範xss 
加入html 轉義


![alt text](detect_img/image-3.png)
測出有問題 訊息太長了  
html 文字匡有限制 但可以繞過前端 所以後端必須也要設限制

