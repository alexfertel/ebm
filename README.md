# Email Based Middleware (EBM)

EBM es un middleware ideado para utilizar Email como capa de transporte

## Instalación
````
pip install ebm  
````
:(

##Uso servidor

##Uso cliente
````
import ebm
ebm = ebm.EBMC('user_client','s@g.com','server.com','pwd')
ebm.register('user','pwd')

ebm.login('user','pwd')

ebm.send('another_user', 'data to send', 'name of the package')

###### Received data are in
ebm.received
````

*By*:

* Alexander Gonzalez
* Sandor Martin
