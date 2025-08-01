# app/services/firewall.py

import os
import requests
from fastapi import Request

# Get credentials from environment
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID")
AZURE_SQL_SERVER_NAME = os.getenv("AZURE_SQL_SERVER_NAME")
AZURE_RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP")


def get_client_ip(request: Request) -> str:
    """Extract IP address from request headers or connection."""
    forwarded = request.headers.get("x-forwarded-for")
    return forwarded.split(",")[0] if forwarded else request.client.host


def get_azure_access_token() -> str:
    """Get Azure AD token using client credentials flow."""
    url = f"https://login.microsoftonline.com/{AZURE_TENANT_ID}/oauth2/v2.0/token"
    headers = { "Content-Type": "application/x-www-form-urlencoded" }
    data = {
        "client_id": AZURE_CLIENT_ID,
        "client_secret": AZURE_CLIENT_SECRET,
        "scope": "https://management.azure.com/.default",
        "grant_type": "client_credentials"
    }
    resp = requests.post(url, headers=headers, data=data)
    resp.raise_for_status()
    return resp.json()["access_token"]


def add_firewall_rule(ip_address: str) -> bool:
    """Add an IP to Azure SQL Server firewall rules."""
    token = get_azure_access_token()
    url = (
        f"https://management.azure.com/subscriptions/{AZURE_SUBSCRIPTION_ID}"
        f"/resourceGroups/{AZURE_RESOURCE_GROUP}/providers/Microsoft.Sql/servers/"
        f"{AZURE_SQL_SERVER_NAME}/firewallRules/Allow_{ip_address.replace('.', '_')}?api-version=2022-05-01-preview"
    )
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "properties": {
            "startIpAddress": ip_address,
            "endIpAddress": ip_address
        }
    }
    try:
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"[❌ Firewall Rule Error] {e}")
        return False
