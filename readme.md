# auto update jellyfin metadata script

This script can be used to (partly) automate the update of the metadata language of Series in Jellyfin.  

## Installation

Download sources, create a virtual environment, install `requirements.txt`  

## Usage

variables

| key                    | mand. | explanation                                                   | default
| ---------------------- | ----- | ------------------------------------------------------------- | ---
| USERID                 | *     | internal UserId - can be found with `GET http://{HOST}/Users` | -
| TOKEN                  | *     | tokenId - create one in the administration                    | -
| HOST                   | *     | host of jellyfin without the protocol. i.e. `jellyfin.local`  | -
| PROTOCOL               |       | protocol. either `http` or `https`                            | `http`
| TARGET_CONFIDENCE      |       | target confidence of the language                             | `0.75` 
| TARGET_LANG            |       | target language                                               | `de`
| CONNECTION_RETRIES     |       | max connection retries in case something goes wrong           | `3`
| CONNECTION_ERROR_DELAY |       | delay between connection retries in seconds                   | `5`

Set those variables either by exporting them or by creating a .env file.  
Be aware that `USERID`, `TOKEN` and `HOST` are mandatory.  
Then just run the `jellyfin-getTvSeries.sh` script.

## Known TODOs

- Go through each item instead of only the series itself.