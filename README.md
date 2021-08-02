# Greenpass Turnstile
Attivare un tornello con il greenpass

## Perché?
Per entrare in sicurezza in un edificio, le persone devono essere vaccinate. Pagare una persona per controllare gli accessi a ogni edificio, pubblico o privato, è troppo costoso, è necessario automatizzare la cosa.
Un tornello di ridotte dimensioni può costare qualche centinaio di euro. L'hardware per eseguire i controlli meno di 100 euro. Con una piccola spesa, ogni edificio può essere reso sicuro.

Questa applicazione può girare su un RaspberryPi, con o senza schermo, e verifica sia la validità di un Green Pass sia la corrispondenza tra il Green Pass e un documento elettronico (es: Tessera Sanitaria).
Per il momento la verifica viene utilizzata solo la Tessera Sanitaria, perché ce l'hanno tutti i cittadini italiani (mentre la CIE o la firma digitale non sono così diffuse).

## TODO
* Pubblicare script per installazione su RaspberryOs
* Modalità di log degli accessi
* Pubblicare codice per attivazione relay
* Sviluppo GUI multilingue
* Supportare il passaporto elettronico come alternativa alla Tessera Sanitaria per i cittadini non italiani
