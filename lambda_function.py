import json
import os
import boto3
from decimal import Decimal
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ.get('TABLE_NAME', 'InventoryItems'))

def decimal_to_native(obj):
    if isinstance(obj, list):
        return [decimal_to_native(i) for i in obj]
    if isinstance(obj, dict):
        return {k: decimal_to_native(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    return obj

def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
        },
        "body": json.dumps(body)
    }

def get_user_groups(event):
    claims = (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("jwt", {})
        .get("claims", {})
    )
    groups = claims.get("cognito:groups", "")
    if isinstance(groups, str):
        return [g.strip() for g in groups.split(",") if g.strip()]
    return groups if isinstance(groups, list) else []

def is_editor(event):
    groups = get_user_groups(event)
    return "editors" in groups

def lambda_handler(event, context):
    method = event.get("requestContext", {}).get("http", {}).get("method", "")
    raw_path = event.get("rawPath", "")
    path_params = event.get("pathParameters") or {}
    item_id = path_params.get("id")

    if method == "OPTIONS":
        return response(200, {"message": "ok"})

    # GET /items
    if method == "GET" and raw_path == "/items":
        result = table.scan()
        items = decimal_to_native(result.get("Items", []))
        return response(200, items)

    # GET /items/{id}
    if method == "GET" and item_id:
        result = table.get_item(Key={"itemId": item_id})
        item = result.get("Item")
        if not item:
            return response(404, {"message": "Item not found"})
        return response(200, decimal_to_native(item))

    # POST /items
    if method == "POST" and raw_path == "/items":
        if not is_editor(event):
            return response(403, {"message": "Write access denied"})
        body = json.loads(event.get("body") or "{}")
        item = {
            "itemId": body["itemId"],
            "itemName": body["itemName"],
            "quantity": int(body["quantity"]),
            "category": body["category"],
            "location": body["location"]
        }
        table.put_item(Item=item)
        return response(201, {"message": "Item created", "item": item})

    # PUT /items/{id}
    if method == "PUT" and item_id:
        if not is_editor(event):
            return response(403, {"message": "Write access denied"})
        body = json.loads(event.get("body") or "{}")
        table.update_item(
            Key={"itemId": item_id},
            UpdateExpression="SET itemName=:n, quantity=:q, category=:c, #loc=:l",
            ExpressionAttributeNames={"#loc": "location"},
            ExpressionAttributeValues={
                ":n": body["itemName"],
                ":q": int(body["quantity"]),
                ":c": body["category"],
                ":l": body["location"]
            }
        )
        return response(200, {"message": "Item updated"})

    # DELETE /items/{id}
    if method == "DELETE" and item_id:
        if not is_editor(event):
            return response(403, {"message": "Write access denied"})
        table.delete_item(Key={"itemId": item_id})
        return response(200, {"message": "Item deleted"})

    return response(404, {"message": "Route not found"})