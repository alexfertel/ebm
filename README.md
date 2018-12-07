# Email Based Middleware (EBM)

EBM es un middleware ideado para utilizar Email como capa de transporte

## Instalación
````
pip install ebm-client  
````
:(

##Uso servidor

##Uso cliente
````
import ebm_client
ebm = ebm_client.EBMC('user_client','s@g.com','server.com','pwd')
ebm.register('user','pwd')

ebm.login('user','pwd')

ebm.send('another_user', 'data to send', 'name of package')

###### Recived data are in
ebm.recived
````

*By*:

* Alexander Gonzalez
* Sandor Martin
