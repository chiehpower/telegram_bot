# Telegram Bot 

Mainly it can handle some actions regarding cloud management such as controlling Compute Engine on GCP.

## Usage 

1. Please provide the permission key file in the assets, and rename as `gcp_key.json` file.
2. Please fill in the all information in the `example.yaml`, and then rename it as `config.yaml` file.
3. Access the server folder.
    ```
    cd server
    ```
4. Launch the server.
    ```
    python3 main.py
    ```
## Features

- [x] Check whole instances of compute engine on GCP.
- [x] List whole instances of compute engine, and delete a specific instance on GCP.
    - [ ] Dynamically fill the zone value from an instance. 
- [ ] Create an instance on GCP.