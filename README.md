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
  - **Escuchar y elegir**: oye la oración y elige la imagen de "después". En el nivel 3 siempre aparece el mismo objeto con otro resultado (por ejemplo, la taza rota), para que se note la diferencia entre 被 y 沒被. En las imágenes de "no pasó nada" aparece el signo ＝.
  - **Elegir la oración correcta**: una frase correcta y dos incorrectas (solo errores que de verdad no se pueden decir, por ejemplo 被 mal colocado; en el nivel 3, el error típico: 被沒 en lugar de 沒被).
  - **把 ⇒ 被** (solo nivel 1): lees una oración con 把 y eliges la oración con 被 que significa lo mismo. Aquí sí aparece una opción con los papeles invertidos (哥哥被麵包吃完了), porque lo que se practica es quién hace qué.
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
- Pendiente: reto mixto 把 + 被 y otros usos de 被.

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
- 題型：**排字卡**、**聽音選圖**、**選出正確的句子**，關卡 1 另有 **把 ⇒ 被** 轉換題
  - 關卡 3 的聽音題一定會有「同一個東西、不同結果」的圖（例如破掉的杯子），讓學生分辨「被打破了」和「沒被打破」；「什麼都沒變」的圖右上角有「＝」
  - 選句子題的錯誤選項只用真正不通順的句子（關卡 3 放最常見的錯：「被沒」）；轉換題才會放主客顛倒的選項，因為要練的就是誰做了什麼
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
- 之後可以加：把和被混合挑戰、被的其他用法

---

由「每天一分鐘 · 一分鐘學中文」製作 · Hecho por Ben (@cadadiaunosminutos_ben_chino)

## 手機瀏覽器備註：捲動後回不到頂端（2026-10-24）
iPhone 版 Chrome 上，頁面可以捲動時，往下捲之後有時回不到最上面（Safari 正常）。
處理方式（已套用在本遊戲）：`<meta name="viewport">` 設 `maximum-scale=1`，不使用 `viewport-fit=cover`；`<html>` 加 `html{color-scheme:light}`。新增頁面請照這個寫。
