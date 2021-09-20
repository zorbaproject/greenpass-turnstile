# Greenpass Turnstile
Attivare un tornello con il greenpass

## Perché?
Per entrare in sicurezza in un edificio, le persone devono essere in possesso di Green Pass. Pagare una persona per controllare gli accessi a ogni edificio, pubblico o privato, è troppo costoso, è necessario automatizzare la cosa.
Un tornello di ridotte dimensioni può costare qualche centinaio di euro. L'hardware per eseguire i controlli meno di 100 euro. Con una piccola spesa, ogni edificio può essere reso sicuro.

Questa applicazione può girare su un RaspberryPi, con o senza schermo, e verifica sia la validità di un Green Pass sia la corrispondenza tra il Green Pass e un documento elettronico (es: Tessera Sanitaria).
Per il momento la verifica viene utilizzata solo la Tessera Sanitaria, perché ce l'hanno tutti i cittadini italiani (mentre la CIE o la firma digitale non sono così diffuse).

## Hardware necessario
* RaspberryPi o computer simile (eventualmente anche un vecchio laptop)
* Webcam FullHD USB con piedistallo o morsa per fissaggio
* Lettore di Smartcard USB
* Altoparlante con cavo Jack
Eventualmente, è possibile aggiungere anche uno schermo HDMI di piccole dimensioni, per esempio quelli da 7 pollici. Se il software deve essere gestito da un operatore fidato, sarà necessaria anche una tastiera USB.

La webcam verrà utilizzata per riconoscere il QR code del Green Pass, quindi va fissata verso il basso, puntando su un piano sul quale gli avventori potranno appoggare il foglio o lo smartphone. La soluzione più economica è un piccolo treppiede appoggiato su un banchetto.

Lo schermo non è fondamentale: il software funziona anche senza uno schermo, emettendo due suoni differenti a seconda del fatto che il Green Pass sia stato riconosciuto oppure no. Se è stato utilizzato uno schermo, il software lo utilizza automaticamente per presentare una anteprima dell'immagine rilevata dalla webcam, così da aiutare il cliente a allineare correttamente il qrcode.

## Installazione
Il software e tutte le sue dipendenze possono essere installati con lo script install.sh. Questo esegue anche lo script autologin, che configura il RaspberryPi in modo da eseguire il software per la verifica del Green Pass ad ogni avvio. In questo modo basta accendere il Raspberry ed è tutto pronto per il riconoscimento dei clienti.

## Configurazione
Al momento sono disponibili due parametri di configurazione nel file json che si trova nello stesso repository del programma principale.
* *log*: Se impostato a "true", registra data e ora e nome (eventualmente anche il cdoice fiscale, si disponibile) di ogni persona. Questo pu essere utile per il contact tracing automatico, nel caso vi sia un caso di persona positiva al Covid nel locale. Ma può essere disabilitato se non si vogliono conservare questi dati personali.
* *interactive*: Se impostato a "true", nel caso in cui l'utente abbia un Green Pass valido ma non abbia presentato una Tessera Sanitaria viene chiesto a un operatore di confermare che l'identità della persona corrisponda al proprietario del Green Pass. Se impostato a "false", il software è completamente autonomo, quindi se non viene inserita una Tessera Sanitaria il Green Pass viene considerato non verificato e l'ingresso è negato.

## TODO
- [x] Pubblicare script per installazione su RaspberryOs
- [x] Modalità di log degli accessi
- [x] Pubblicare codice per attivazione relay
- [ ] Sviluppo GUI multilingue
- [ ] Supportare il passaporto elettronico come alternativa alla Tessera Sanitaria per i cittadini non italiani
