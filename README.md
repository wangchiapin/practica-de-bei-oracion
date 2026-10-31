# 被 · Oración con 被
### Práctica de la oración pasiva con 被 (被字句) para hispanohablantes · 給西語學習者的被字句練習遊戲

🎮 **Jugar / 開始玩:** https://wangchiapin.github.io/practica-de-bei-oracion/
(需要先在這個 repo 的 Settings → Pages 把來源設成 `main`，根目錄)

El juego hermano de **把** · https://wangchiapin.github.io/practica-de-ba-oracion/

---

## 🇪🇸 Español

**被 (Oración con 被)** es un juego web para practicar la pasiva en chino mandarín. En cada pregunta ves dos imágenes, **antes** y **después**, y debes formar o reconocer la oración correcta. Usa las mismas imágenes del juego **把**: es el mismo hecho, contado desde el otro lado.

> 東西 + **被** + 誰 + 動作 + 結果 + 了  
> Ejemplo: 杯子**被**他打破了。 (La taza fue rota por él.)

### Cómo se juega
- En la **pantalla de inicio** escribes tu **apodo** (obligatorio), eliges el nivel y juegas. Los textos de la interfaz se ven en dos líneas: chino grande y español/inglés pequeño.
- **4 niveles** con un banco de oraciones que sigue creciendo (cada partida elige 10 al azar):
  1. **關卡 1 · Nivel 1** – se dice quién lo hizo: 碗被弟弟打破了
  2. **關卡 2 · Nivel 2** – no se dice quién lo hizo: 手機被摔壞了
  3. **關卡 3 · Nivel 3** – la negación va **antes** de 被 (沒被、沒有被、還沒被): 杯子沒被打破 / 蛋糕還沒被吃完
  4. **關卡 4 · Nivel 4** – cosas que todavía no pasan: **會被** (杯子會被弟弟打破) y **不要被** (衣服不要被雨淋濕). Estas oraciones no llevan 了. Imágenes propias: izquierda = "ahora", derecha = "después"; en 不要被 la imagen de "después" lleva una ✕ roja ("que no pase").
- Los tipos de pregunta:
  - **Ordenar tarjetas**: mira las imágenes y ordena las palabras.
  - **Escuchar y elegir**: oye la oración y elige la imagen de "después". En el nivel 3 siempre aparece el mismo objeto con otro resultado (por ejemplo, la taza rota), para que se note la diferencia entre 被 y 沒被. En las imágenes de "no pasó nada" el «antes» y el «después» son idénticos (ya no se dibuja el signo ＝, porque delataba la respuesta).
  - **Elegir la oración correcta**: una frase correcta y dos incorrectas (solo errores que de verdad no se pueden decir, por ejemplo 被 mal colocado; en el nivel 3, el error típico: 被沒 en lugar de 沒被).
- Todas las imágenes están dibujadas con código (SVG), con un estilo sencillo y limpio.

### Puntos
| Acción | Puntos |
|---|---|
| Correcta a la primera | 100 (con racha ×1.2 y ×1.5) |
| Bonus de rapidez (primeros 10 s) | hasta +50 |
| Correcta en el segundo intento | 50 |
| Usar "Pista" (traducción) | −20 |
| Usar el mini diccionario | sin penalización |

No hay vidas. **Estrellas** según las respuestas correctas a la primera (50 %, 70 % y 90 %). Los cuatro niveles están abiertos desde el principio. Al final hay un **repaso de errores** y un **ranking** (mejor puntaje por jugador, top 10).

### Idiomas y lectura
Igual que el juego 把: interfaz **Español / English / solo chino**, **繁體 / 简体**, lectura en **pinyin / zhuyin (注音) / ambos / sin lectura** con pronunciación de Taiwán, voz `zh-TW` en tres velocidades. Los ajustes se comparten con los demás juegos mediante `localStorage` (`hanziGames.settings`). Nombre, progreso y ranking se guardan aparte (`bei_cfg`, `bei_prog`, `bei_lb`).

### Para profesores
- Es un solo archivo: `index.html`. Funciona en GitHub Pages sin compilar nada.
- Las imágenes y los datos de cada oración vienen del juego 把: cada oración 被 apunta a una escena de 把 (`BEI_DEF`, primer número). Para agregar oraciones, añade una fila en `BEI_DEF` con una escena que ya exista. La biblioteca de imágenes (`OB`, `PL`, `RAW2`/`RAW3`, `SPEC`, `KEYS`…) es una copia de la de 把: si se dibujan escenas nuevas en 把, hay que copiarlas aquí también, junto con `SIMSET` (parejas de imágenes parecidas que no deben salir juntas en «Escuchar y elegir»).
- La carpeta `docs/` guarda la tabla de revisión de las oraciones nuevas (`新增句子_請審查.csv`).
- **Ranking compartido (Firebase Firestore):** conectado al proyecto `memorma-24dab` (el mismo de 把, Memorama y Ordena el Armario), con inicio de sesión anónimo; los puntajes se guardan en la colección `beiLeaderboard` (mejor puntaje de cada uno de los cuatro niveles, suma total, 10 mejores). La configuración está en `FIREBASE_CONFIG` de `index.html`; si no se puede conectar, el ranking solo se guarda en el dispositivo. Las visitas y las partidas se registran como en los otros juegos, con el código `bei`.
- El nivel 4 (`F_DEF`) no sale del juego 把: cada oración trae sus propias tarjetas y usa imágenes nuevas (`SC.fA`, `fB`, `fC`, `fD`; con ✕ para 不要被). Para agregar oraciones, añade una fila en `F_DEF` con una imagen que ya exista; una imagen nueva se dibuja en el mismo estilo.
- **Modo clase (hecho; abrir/cerrar lo decide el interruptor del Centro de profesores):** si el enlace lleva `?class=` + código de clase (el profesor lo genera en el «Centro de profesores»), el resultado de cada nivel se envía al profesor: se guarda en `class_scores` del proyecto central `subscription-48d3c` (una entrada por alumno y por nivel, solo la mejor puntuación; `game:'bei'`). El juego no tiene interruptor propio: todo lo decide el interruptor de mantenimiento del Centro de profesores (`portalStatus/center-bei`; sin documento = en mantenimiento, `off:false` = abierto). En mantenimiento, los enlaces de clase muestran «en mantenimiento», no se puede jugar y no se guardan resultados (`?preview` exceptuado). Sin `?class=` el juego funciona igual que siempre.
- **Reporte de preguntas:** el botón «🚩 Algo raro» (这题怪怪的) en cada pregunta envía el reporte (motivo, nota, imágenes, oración) a `game_reports` del proyecto central `subscription-48d3c` (`game:'bei'`); solo Ben lo ve, en «Problemas reportados» de `stats.html` del sitio de enlaces.
- **Vista previa al compartir:** `og.jpg` (1200×630) y las etiquetas `og:` del `<head>` (título «被 · oración con 被»).
- Pendiente: reto mixto 把 + 被, la pregunta «把 ⇒ 被» (el código `T` sigue en el archivo pero está desactivado; falta una oración con 把 para cada nivel) y otros usos de 被.

---

## 🇹🇼 繁體中文

**被** 是一個練習「被字句」的網頁小遊戲。每題會看到「之前」和「之後」兩張圖，學生要排出或認出正確的句子。圖片和「把」遊戲共用：同一件事，從另一邊來說。

> 東西 ＋ **被** ＋ 誰 ＋ 動作 ＋ 結果 ＋ 了

### 玩法
- **首頁只有一頁**：輸入暱稱（必填）、選關卡、開始玩；介面文字分兩行，上面中文大字、下面西文／英文小字
- 共 **4 關**，題庫會持續增加（每次遊玩隨機抽 10 題）：
  1. 關卡 1：有說是誰做的（碗被弟弟打破了）
  2. 關卡 2：沒說是誰做的（手機被摔壞了）
  3. 關卡 3：否定詞放在「被」前面（杯子沒被打破、蛋糕還沒被吃完）
  4. 關卡 4：還沒發生的事，用「會被」和「不要被」（杯子會被弟弟打破、衣服不要被雨淋濕）；句子後面沒有「了」。圖左邊是「現在」、右邊是「之後」，不要被的右圖加紅色 ✕，意思是「不要變成這樣」
- 題型：**排字卡**、**聽音選圖**、**選出正確的句子**
  - 關卡 3 的聽音題一定會有「同一個東西、不同結果」的圖（例如破掉的杯子），讓學生分辨「被打破了」和「沒被打破」；「什麼都沒變」的「之前」「之後」兩張圖完全一樣（已拿掉「＝」記號，因為會洩漏答案）
  - 選句子題的錯誤選項只用真正不通順的句子（關卡 3 放最常見的錯：「被沒」）
- 圖片全部用程式碼繪製，風格簡單乾淨

### 計分與結束
- 第一次答對 100 分，連續答對有加成；10 秒內答對最多再加 50 分；第二次才答對得 50 分；看「提示」扣 20 分，查「小字典」不扣分
- 不扣命，每關 10 題；依第一次就答對的比例給 1～3 顆星（50%、70%、90%）；四個關卡一開始就全部開放
- 結算有錯題複習，另有排行榜（每人只留最高分，前 10 名）

### 語言與讀音
和「把」遊戲一樣：Español／English／只有中文、繁體／简体、拼音／注音／兩個都顯示／不顯示（台灣讀音）、語音三種語速；設定與其他遊戲共用 `hanziGames.settings`。

### 老師設定
- 單一檔案 `index.html`，放在 GitHub Pages 即可使用（Settings → Pages → main，根目錄）
- 每個被字句都對應「把」遊戲的一個場景（`BEI_DEF` 的第一個數字）；要新增句子，在 `BEI_DEF` 加一行、用已經有的場景即可。圖庫（`OB`、`PL`、`RAW2`／`RAW3`、`SPEC`、`KEYS` 等）是從「把」遊戲複製來的：如果「把」新畫了場景，這裡也要一起複製過來，並更新 `SIMSET`（圖片太像、聽音題不要同時出現的組合）
- `docs/` 資料夾放新增句子的審查表（`新增句子_請審查.csv`）
- 排行榜已接到 Firebase 專案 `memorma-24dab`（與「把」、翻牌記憶、收納小達人共用，匿名登入，集合 `beiLeaderboard`，四個關卡各留最高分、加總排名，前 10 名）；設定在 `index.html` 的 `FIREBASE_CONFIG`，連不上時只存在該裝置；訪客和遊玩紀錄比照其他遊戲，用代號 `bei` 記錄
- 關卡 4（`F_DEF`）不是從「把」遊戲來的：每句自己帶字卡，圖是新畫的（`SC.fA`、`fB`、`fC`、`fD`，不要被的圖有 ✕）；新增句子就在 `F_DEF` 加一行、用已經有的圖，需要新圖時照同樣風格再畫
- **班級模式（已做好，開不開放由老師管理中心的維修開關決定）**：連結帶 `?class=班級碼`（老師在「老師管理中心」產生）時，每關成績會回傳給老師，存到中央專案 `subscription-48d3c` 的 `class_scores`（每位學生每一關一筆，只留最高分，`game:'bei'`）。遊戲本身沒有自己的開關，全由老師管理中心的維修開關（`portalStatus/center-bei`，沒有設定＝預設維修中、`off:false`＝開放）決定：維修中時老師中心的卡片變淡、班級連結顯示「🔧 維修中」不能玩也不記成績（`?preview` 例外）。沒有 `?class=` 時遊戲跟原來一樣
- **題目回報**：每題有「🚩 這題怪怪的」按鈕，送出（原因、備註、圖、題目句）到中央專案 `subscription-48d3c` 的 `game_reports`（`game:'bei'`）；只有 Ben 在分享區 `stats.html` 的「問題回報」看得到
- **分享連結預覽**：`og.jpg`（1200×630）加 `<head>` 裡的 og 標籤（標題「被 · oración con 被」）
- 之後可以加：把和被混合挑戰、「把 ⇒ 被」轉換題（程式 `T` 還在、目前停用，每一關都要有對應的把句子）、被的其他用法

---

由「每天一分鐘 · 一分鐘學中文」製作 · Hecho por Ben (@cadadiaunosminutos_ben_chino)

## 手機瀏覽器備註：捲動後回不到頂端（2026-10-24）
iPhone 版 Chrome 上，頁面可以捲動時，往下捲之後有時回不到最上面（Safari 正常）。
處理方式（已套用在本遊戲）：`<meta name="viewport">` 設 `maximum-scale=1`，不使用 `viewport-fit=cover`；`<html>` 加 `html{color-scheme:light}`。新增頁面請照這個寫。

- GA 事件名稱（2026-10-29 起）：`bei_start`、`bei_level_start`、`bei_answer`、`bei_level_end`（之前誤用把的 `ba_` 開頭，所以舊資料裡被的事件混在把的統計裡）。

## 測試

`PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 tests/test_game.py`（Python + Playwright；擋掉外部網路，用假的 Firebase 和假的語音，不碰真的資料庫）

- 目前 160 項檢查（2026-10-30 建立）。
- 涵蓋：維修開關（`portalStatus/center-bei`）、`?preview`、`?class=`、四關全開、整關解題、計分、星等門檻（50／70／90%）、設定每個值、公開排行榜、班級成績、題目回報。與「把」是同一套程式的測試。
- 改了遊戲的計分、設定、排行榜或畫面文字後，推上去之前先跑一次。
- 驗證方式：另外複製一份遊戲、故意改壞一個地方，測試會出現 FAIL。

## 自訂句庫模式（`?bank=句庫碼`）
- 老師在「老師管理中心」的「自訂句庫」挑句子（只存句子編號，在中央專案 `shared_babanks/{句庫碼}`）；連結帶 `?bank=` 時首頁只有名字欄＋一張「開始」卡片（上方顯示句庫名稱），沒有關卡卡片、排行榜、老師入口。
- 句庫也可以含老師自己寫的句子（`shared_babanks` 的 `custom` 欄，每句 `{tk:['繁|簡|拼音|注音',…],es,en}`，沒有圖）：這類句子只出文字題（看翻譯排卡片／聽句選句子／看翻譯選句子），錯誤選項取自同句庫的其他句子；不出現「這題怪怪的」回報；資料先清掉 < > 等符號才用。
- 自訂句子可以有圖（訂閱老師加；圖存在 `shared_babimgs/{句庫碼}_{1|2}`，句子的 `im` = 1或2＋圖片代號）：有圖的句子出看圖排卡片／看圖選句子／聽句選圖（句庫要有 ≥3 張圖，否則改文字聽句題）；圖片只收 JPEG 的 data URL，其他一律不用；讀不到就當沒有圖。圖片用 localStorage（`babimg_句庫碼`）記在裝置上，版本＝句庫文件的 `updatedAt`，沒更新就不再下載（省 Firebase 傳出流量）。
- 每次從句庫隨機抽 10 題（題型比例照原本），不動原本關卡的星星進度、不寫公開排行榜。句庫裡已不存在的句子編號會略過。
- 加 `&class=班級碼` 時成績回傳老師，`class_scores` 的 `k` ＝句庫碼；`?preview` 不回傳成績且不受維修影響。維修中、句庫失效、連不上雲端都有提示（同班級模式）。
- `sentences.json`：老師中心挑句子用的句子清單，由 `tools/make_sentences.py` 從 `index.html` 的 `DATA` 產生；**句子有增減後要重新執行 `python3 tools/make_sentences.py`**，`tests/test_game.py` 會檢查清單有沒有過期。
