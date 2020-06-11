# Docker-compose API
  
## Description
A Flask-RESTful API for retrieving information about variants from gnomAD. Makes usages of docker-compose to orchestrate the mongoDB container with the API container.

## Installation 

### Prerequisites
* Docker
* Docker-compose
* git

#### Set-up
1. `git clone https://zero.han.nl/gitlab/Jordan.Dekker/data_integratie_api.git`
2.  Start the application: `docker-compose up`
3.  Go to the IP address 127.0.0.1:5000
4.  Stop the application: `Ctrl-C` and `docker-compose down`


## Usage
Single API requests.

| resource      | description                             |
|---------------|-----------------------------------------|
| /variant/{id} | Returns a single variant with gnomAD id |
| /list         | Returns all variants in database        |
| /id/{id}      | Returns all variants from query id.     |
| /query?       | See below                               |


Parameters used for the `/query?` resource:

| parameter      | description                |
|----------------|----------------------------|
| chromosome={#} | filter specific chromosome |
| position={#}   | filter specific position   |
| position={#-#} | filter range position      |
| reference={c}  | filter specific reference  |
| alternate={c}  | filter specific alternate  |

for example `http://127.0.0.1:5000/query?chromosome=21&reference=C&alternate=T&position=9825814-15025814`


## Contact Information
*  Jordan Dekker jl.dekker@student.han.nl
