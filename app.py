#!/usr/bin/env python3
import secrets
import time
import httpx
from urllib.parse import urlencode

from nicegui import ui, app
from fastapi import Request

from page_router import Router

AUTH_BASE_URL = "https://app.clio.com/oauth/authorize"
TOKEN_URL = "https://app.clio.com/oauth/token"
DEAUTHORIZE_URL = "https://app.clio.com/oauth/deauthorize"

HOST = "127.0.0.1"
PORT = 8080

REDIRECT_URI = "http://127.0.0.1:8080/callback"

API_GATEWAY_KEY = "api_gateways"
ACCESS_TOKEN_KEY = "access_tokens"

def load_api_gateways():
    """Load stored API gateway data or initialize default values with unique IDs."""
    stored_data = app.storage.general.get(API_GATEWAY_KEY, {
        "columns": ["ID", "Name", "Client Id", "Client Secret"],
        "rows": []
    })

    # Convert column names to AG Grid column definitions
    column_definitions = []
    for col in stored_data["columns"]:
        col_field = col.lower().replace(" ", "_")

        # Custom properties for ID column
        if col == "ID":
            column_definitions.append({
                "headerName": col,
                "field": col_field,
                "editable": False,
                "checkboxSelection": True,
                "width": 30,  # Fixed width for ID column
                "resizable": True
            })
        else:
            column_definitions.append({
                "headerName": col,
                "field": col_field,
                "editable": True
            })

    # Convert row lists to dictionaries (including ID)
    columns = [col.lower().replace(" ", "_") for col in stored_data["columns"]]
    rows = [dict(zip(columns, row)) for row in stored_data["rows"]]

    return columns, column_definitions, rows

@app.get("/callback")
async def callback(request: Request):
    """Handle OAuth callback, validate state, and request access token."""
    query_params = request.query_params
    code = query_params.get("code")
    state = query_params.get("state")

    if not code or not state:
        return ui.notify("Invalid request: Missing code or state.", type="warning")

    state_key = f"oauth_state_{state}"
    state_data = app.storage.general.get(state_key)

    if not state_data:
        return ui.notify("Invalid or expired state.", type="warning")

    timestamp = state_data.get("timestamp", 0)
    
    # State token set to expire after 60 seconds
    # Removes state token before completing callback 
    if time.time() - timestamp > 60:
        del app.storage.general[state_key]
        return ui.notify("State expired. Please try again.", type="warning")

    client_id = state_data.get("client_id")
    client_secret = state_data.get("client_secret")
    api_gateway = state_data.get("api_gateway")  # Retrieve API Gateway name

    if not client_id or not client_secret:
        del app.storage.general[state_key]
        return ui.notify("Stored client credentials missing. Please restart authentication.", type="warning")

    del app.storage.general[state_key]  # Remove state after use

    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_URL, data=payload, headers=headers)

    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")

        # Store access token in app storage
        access_token_list = app.storage.general.get(ACCESS_TOKEN_KEY, [])
        new_token_entry = {
            "id": len(access_token_list) + 1,
            "api_gateway": api_gateway,
            "access_token": access_token
        }
        access_token_list.append(new_token_entry)
        app.storage.general[ACCESS_TOKEN_KEY] = access_token_list
        return "Success"

    else:
        return "Error"

# Built on the single page application example
# https://github.com/zauberzeug/nicegui/blob/main/examples/single_page_app/main.py

@ui.page('/')  # normal index page (e.g. the entry point of the app)
@ui.page('/{_:path}')  # all other pages will be handled by the router but must be registered to also show the SPA index page
async def main():    
    router = Router()

    @router.add('/')
    async def api_gateways():
        
        """Render API Gateways table with actions."""
        columns, column_definitions, rows = load_api_gateways()

        gateway_table = ui.aggrid({
            "columnDefs": column_definitions,
            "rowData": rows,
            "rowSelection": "single",
            "stopEditingWhenCellsLoseFocus": True,
        })

        def update_storage():
            """Persist rows to storage."""
            app.storage.general[API_GATEWAY_KEY] = {"columns": columns, "rows": [list(row.values()) for row in rows]}
            gateway_table.update()

        def open_add_row_dialog():
            """Opens a dialog box to collect user input for a new row."""
            with ui.dialog() as dialog, ui.card().classes('w-full'):
                ui.label("Add API Gateway")
                name_input = ui.input(label="Name").classes('w-full')
                client_id_input = ui.input(label="Client ID").classes('w-full')
                client_secret_input = ui.input(label="Client Secret").classes('w-full')

                with ui.row():
                    ui.button("Add", on_click=lambda: add_row(name_input.value, client_id_input.value, client_secret_input.value, dialog))
                    ui.button("Cancel", on_click=dialog.close)

                dialog.open()

        def add_row(name, client_id, client_secret, dialog):
            """Adds a new row based on dialog input."""
            if not name or not client_id or not client_secret:
                ui.notify("All fields are required!", type="warning")
                return

            new_id = max((row["id"] for row in rows), default=0) + 1  # Ensure unique ID
            new_row = {"id": new_id, "name": name, "client_id": client_id, "client_secret": client_secret}
            rows.append(new_row)
            update_storage()
            dialog.close()
            ui.notify(f"Added new API Gateway: {name}")

        def handle_cell_value_change(e):
            """Handles inline cell edits and updates storage."""
            updated_row = e.args["data"]
            for i, row in enumerate(rows):
                if row["id"] == updated_row["id"]:
                    rows[i] = updated_row 
                    break
            update_storage()
            ui.notify(f"Updated row: {updated_row}")

        async def delete_selected():
            """Deletes the single selected row and updates storage."""
            selected_rows = await gateway_table.get_selected_rows()

            if not selected_rows:
                ui.notify("No row selected for deletion!", type="warning")
                return

            selected_id = selected_rows[0]["id"]

            nonlocal rows 
            rows[:] = [row for row in rows if row["id"] != selected_id]

            update_storage()
            ui.notify(f"Deleted row with ID: {selected_id}")

        async def create_access_token():
            """Fetch client ID, store credentials with state, and open the OAuth URL in a new tab."""
            selected_rows = await gateway_table.get_selected_rows()

            if not selected_rows:
                ui.notify("No row selected for access token creation!", type="warning")
                return

            selected_row = selected_rows[0]
            client_id = selected_row.get("client_id")
            client_secret = selected_row.get("client_secret")
            api_gateway= selected_row.get("name")

            if not client_id or not client_secret:
                ui.notify("Client ID or Client Secret is missing!", type="warning")
                return

            # Generate a random state token
            state = secrets.token_urlsafe(16)
            timestamp = time.time()

            # Store state, timestamp, client ID, and client secret in storage
            app.storage.general[f"oauth_state_{state}"] = {
                "timestamp": timestamp,
                "client_id": client_id,
                "client_secret": client_secret,
                "api_gateway": api_gateway
            }

            # Construct the OAuth URL
            params = {
                "response_type": "code",
                "client_id": client_id,
                "redirect_uri": REDIRECT_URI,
                "state": state
            }
            auth_url = f"{AUTH_BASE_URL}?{urlencode(params)}"

            # Open the URL in a new tab
            ui.navigate.to(auth_url, new_tab=True)

        gateway_table.on("cellValueChanged", handle_cell_value_change)

        # Buttons for adding and deleting rows
        ui.button("Add API Gateway", on_click=open_add_row_dialog)
        ui.button("Delete Selected", on_click=delete_selected)
        ui.button("Create Access Token", on_click=create_access_token)

    @router.add('/access_tokens')
    def access_tokens():
        """Render the Access Tokens table with a reload button and copy functionality."""

        # Function to load stored access tokens
        def load_access_tokens():
            return app.storage.general.get(ACCESS_TOKEN_KEY, [])

        # AG Grid column definitions
        column_definitions = [
            {"headerName": "ID", "field": "id", "checkboxSelection": True, "width": 30},
            {"headerName": "API Gateway", "field": "api_gateway"},
            {"headerName": "Access Token", "field": "access_token"},
        ]

        # Initialize AG Grid with stored tokens
        token_table = ui.aggrid({
            "columnDefs": column_definitions,
            "rowData": load_access_tokens(),
            "rowSelection": "single",
            "stopEditingWhenCellsLoseFocus": True,
        })

        async def copy_selected_token():
            """Copies the selected access token to clipboard."""
            selected_rows = await token_table.get_selected_rows()

            if not selected_rows:
                ui.notify("No access token selected!", type="warning")
                return

            selected_token = selected_rows[0]["access_token"]

            ui.run_javascript(f'navigator.clipboard.writeText("{selected_token}")')
            ui.notify("Access token copied to clipboard!")

        async def delete_selected_token():
            """Deauthorize and delete the selected access token."""
            selected_rows = await token_table.get_selected_rows()

            if not selected_rows:
                ui.notify("No access token selected for deletion!", type="warning")
                return

            selected_token = selected_rows[0]["access_token"]
            selected_id = selected_rows[0]["id"]

            # Deauthorize token before deletion
            headers = {
                "Authorization": f"Bearer {selected_token}",
                "Content-Type": "application/x-www-form-urlencoded",
            }
            data = {"token": selected_token}

            async with httpx.AsyncClient() as client:
                response = await client.post(DEAUTHORIZE_URL, headers=headers, data=data)

            if response.status_code == 200:
                # Remove the token from storage after successful deauthorization
                access_token_list = app.storage.general.get(ACCESS_TOKEN_KEY, [])
                access_token_list = [token for token in access_token_list if token["id"] != selected_id]
                app.storage.general[ACCESS_TOKEN_KEY] = access_token_list

                token_table.options["rowData"] = access_token_list
                token_table.update()

                ui.notify(f"Deauthorized: {selected_token}")
            else:
                ui.notify(f"Failed to deauthorize access token. Status: {response.status_code}", type="warning")

        def reload_table():
            """Refreshes the table data by loading stored access tokens."""
            token_table.options["rowData"] = load_access_tokens()
            token_table.update()
            ui.notify("Access token table reloaded.")

        ui.button("Reload Table", on_click=reload_table)
        ui.button("Deauthorize Token", on_click=delete_selected_token)
        ui.button("Copy Token", on_click=copy_selected_token)


    with ui.header().classes('row justify-between items-center') as header:
        
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white dense')

        with ui.row().classes('justify-center items-center gap-4'):
            with ui.row().classes('items-center gap-2'):
                ui.label("Redirect URI:")
                ui.button(REDIRECT_URI, on_click=lambda: (
                    ui.notify("Copied to clipboard!"),
                    ui.run_javascript(f'navigator.clipboard.writeText("{REDIRECT_URI}")')
                )).props('no-caps')

            ui.button("Clio API Access", on_click=lambda: ui.navigate.to("https://developers.clio.com/", new_tab=True))\
                .props('dense no-caps')

    with ui.left_drawer().classes('bg-blue-100') as left_drawer:

        ui.button('API Gateways', on_click=lambda: router.open(api_gateways)).classes('w-full')
        ui.button('Access Tokens', on_click=lambda: router.open(access_tokens)).classes('w-full')
        
    # this places the content which should be displayed
    router.frame().classes('w-full p-4 bg-gray-100')

ui.run(host=HOST, port=PORT, title="Clio Access Token Manager")

